import scipy.signal as signal
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn import linear_model
import xarray as xr

# Parameters

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

    # Dependent Variable (DV)

    # Sea Ice Index Data
    dataset_path = rel_path + "S_Sea_Ice_Index_Regional_Monthly_Data_G02135_v3.0.xlsx"

    sectors[sector] = pd.read_excel(dataset_path, sheet_name = sector + "-Extent-km^2")[month_list].head(-1).tail(-3).reset_index(drop=True).apply(pd.to_numeric)
    sectors[sector] = sectors[sector].interpolate(method='linear')

dv = {}
for month in month_list:
    dv[month] = pd.DataFrame({"ENSO": df_soi[month], "PDO": df_pdo[month], "SSR": df_ssr[month]})

# Standardizing dv values
scaler = StandardScaler()

for month, df in dv.items():
    dv[month] = pd.DataFrame(scaler.fit_transform(df), columns=df.columns)

def perform_mlr(iv, dv):
    coeffs = {}
    for month in iv.columns:
        x = dv[month]
        y = iv[month]

        model = linear_model.LinearRegression()
        model.fit(x, y)

        coeffs[month] = {'const': model.intercept_, 'ENSO': model.coef_[0], 'PDO': model.coef_[1], 'SSR': model.coef_[2]}
    return coeffs

coeffs = {}
for region, iv in sectors.items():
    coeffs[region] = perform_mlr(iv, dv)

for region, coeffs in coeffs.items():
    print(f"\nEquations for {region} region:")
    for month, coeff in coeffs.items():
        equation = f"Sea Ice Extent = {coeff['const']} + {coeff['ENSO']}*(ENSO) + {coeff['PDO']}*(PDO) + {coeff['SSR']}*(SSR)"
        print(f"{month}: {equation}")