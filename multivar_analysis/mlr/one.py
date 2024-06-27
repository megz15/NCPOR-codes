import scipy.signal as signal
import pandas as pd
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.linear_model import LinearRegression
import xarray as xr
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# Parameters

poly_deg = 2

# Butterworth Filter
bw_order  = 1     # Filter order
bw_cfreq  = 0.4   # Cutoff frequency
B, A = signal.butter(bw_order, bw_cfreq, btype='low', analog=False)

sectors = {"Bell-Amundsen": None, "Indian": None, "Pacific": None, "Ross": None, "Weddell": None}
rel_path = "../../data/"

regions = {
    'Ross': {'lon': (160, -130), 'lat': (-50, -72)},
    'Bell-Amundsen': {'lon': (-130, -60), 'lat': (-50, -72)},
    'Weddell': {'lon': (-60, 20), 'lat': (-50, -72)},
    'Indian': {'lon': (20, 90), 'lat': (-50, -72)},
    'Pacific': {'lon': (90, 160), 'lat': (-50, -72)}
}

month_list = [
    'January',
    'February',
    'March',
    'April',
    'May',
    'June',
    'July',
    'August',
    'September',
    'October',
    'November',
    'December'
]

columns = ['Year'] + month_list

# Independent Variables (IVs)

# ENSO Data
dataset_path = rel_path + "darwin.anom_.txt"
df_soi = pd.read_csv(dataset_path, delim_whitespace=True, names=columns)
df_soi = df_soi[df_soi['Year']>=1979].head(-1).drop('Year', axis=1).reset_index(drop=True)

# PDO Data
dataset_path = rel_path + "ersst.v5.pdo.dat"
df_pdo = pd.read_csv(dataset_path, delim_whitespace=True, names=columns)
df_pdo = df_pdo[df_pdo['Year']>=1979].head(-1).drop('Year', axis=1).reset_index(drop=True)

# IOD Data
df_iod = pd.read_pickle('iod/iod.pkl')

for sector in list(sectors.keys()):

    # SSR Data
    dataset_path = rel_path + 'netcdf/rad/radiation_1979-2023_monthly_seaice.nc'
    with xr.open_dataset(dataset_path) as ds:
        resampled_ds = ds['ssr'].sel(
            longitude = slice(
                min(regions[sector]['lon']), max(regions[sector]['lon'])
            ), latitude = slice(
                max(regions[sector]['lat']), min(regions[sector]['lat'])
            )).mean(dim=['latitude', 'longitude'])
        
        df_ssr = resampled_ds.to_dataframe().reset_index()
        
        df_ssr['Year'] = df_ssr['time'].dt.year
        df_ssr['Month'] = df_ssr['time'].dt.strftime('%B')
        
        df_ssr = df_ssr.pivot(index='Year', columns='Month', values='ssr')
        df_ssr.reset_index(inplace=True)

    # STR Data
    dataset_path = rel_path + 'netcdf/rad/radiation_1979-2023_monthly_seaice.nc'
    with xr.open_dataset(dataset_path) as ds:
        resampled_ds = ds['str'].sel(
            longitude = slice(
                min(regions[sector]['lon']), max(regions[sector]['lon'])
            ), latitude = slice(
                max(regions[sector]['lat']), min(regions[sector]['lat'])
            )).mean(dim=['latitude', 'longitude'])
        
        df_str = resampled_ds.to_dataframe().reset_index()
        
        df_str['Year'] = df_str['time'].dt.year
        df_str['Month'] = df_str['time'].dt.strftime('%B')
        
        df_str = df_str.pivot(index='Year', columns='Month', values='str')
        df_str.reset_index(inplace=True)

    # Dependent Variable (DV)

    # Sea Ice Index Data
    dataset_path = rel_path + "S_Sea_Ice_Index_Regional_Monthly_Data_G02135_v3.0.xlsx"

    sectors[sector] = pd.read_excel(dataset_path, sheet_name = sector + "-Extent-km^2")[month_list].head(-1).tail(-3).reset_index(drop=True).apply(pd.to_numeric)
    sectors[sector] = sectors[sector].interpolate(method='linear')

dv = {}
for month in month_list:
    dv[month] = pd.DataFrame({"ENSO": df_soi[month], "PDO": df_pdo[month], "SSR": df_ssr[month], "STR": df_str[month], "IOD": df_iod[month]})

# Standardizing dv values
scaler = StandardScaler()

for month, df in dv.items():
    dv[month] = pd.DataFrame(scaler.fit_transform(df), columns=df.columns)

def perform_mlr(iv, dv):
    coeffs = {}
    for month in iv.columns:
        x = dv[month]
        y = iv[month]

        poly = PolynomialFeatures(degree=poly_deg)
        x_poly = poly.fit_transform(x)

        model = LinearRegression()
        model.fit(x_poly, y)

        coeffs[month] = dict(zip(poly.get_feature_names_out().tolist(), model.coef_.tolist()))
        del coeffs[month]['1']
        coeffs[month] = {'const':model.intercept_, **coeffs[month]}

        # y_pred = model.predict(x_poly)
        # coeffs[month] = y_pred
    return coeffs

coeffs = {}
for region, iv in sectors.items():
    coeffs[region] = perform_mlr(iv, dv)

for region, coeffs in coeffs.items():
    print(f"\n\nEquations for {region} region:")
    for month, coeff in coeffs.items():
        print(f'\n{month}:\n' + ' + '.join([f'{coeff[x]}*({x})' if x!='const' else str(coeff[x]) for x in coeff]))
        # print(f'{month} : {coeff}')

# # Predictions
# for region, pred_dict in coeffs.items():
#     print(f"Predictions for {region} region:\n")
#     for month, pred in pred_dict.items():
#         actual = sectors[region][month]
#         comparison_df = pd.DataFrame({'Actual': actual, 'Predicted': pred})
#         print(f"Month: {month}")
#         print(comparison_df)
#         print("\n")