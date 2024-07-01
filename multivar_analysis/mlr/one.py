from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.linear_model import LinearRegression
import pandas as pd

# Parameters

poly_deg = 1

rel_path = "../../data/"

sectors = {
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

df_soi = pd.read_pickle('pickles/soi.pkl')
df_pdo = pd.read_pickle('pickles/pdo.pkl')
df_iod = pd.read_pickle('pickles/iod.pkl')
df_ssr = pd.read_pickle('pickles/ssr.pkl')
df_str = pd.read_pickle('pickles/str.pkl')

# Dependent Variable (DV)

df_sie = pd.read_pickle('pickles/sie.pkl')

dv = {}
for month in month_list:
    dv[month] = pd.DataFrame({"ENSO": df_soi[month], "PDO": df_pdo[month], "IOD": df_iod[month]})

# Standardizing dv values
scaler = StandardScaler()

for month, df in dv.items():
    dv[month] = pd.DataFrame(scaler.fit_transform(df), columns=df.columns)

def perform_mlr(iv, dv, region_dv):
    coeffs = {}
    for month in month_list:
        for i in list(region_dv.keys()):
            dv[month][i] = region_dv[i][month]

        x = dv[month]
        y = iv[month]

        poly = PolynomialFeatures(degree=poly_deg)
        x_poly = poly.fit_transform(x)

        model = LinearRegression()
        model.fit(x_poly, y)

        coeffs[month] = dict(zip(poly.get_feature_names_out().tolist(), model.coef_.tolist()))
        del coeffs[month]['1']
        coeffs[month] = {'const':model.intercept_, **coeffs[month]}
    return coeffs

coeffs = {}
for sector in list(sectors.keys()):
    df_sie_r = df_sie[df_sie['Sector'] == sector].reset_index(drop=True)
    df_ssr_r = df_ssr[df_ssr['Sector'] == sector].reset_index(drop=True)
    df_str_r = df_str[df_str['Sector'] == sector].reset_index(drop=True)

    df_sie_r = df_sie_r.drop(columns = ['Sector', 'Year']).reset_index(drop=True)

    coeffs[sector] = perform_mlr(df_sie_r, dv, {
        'SSR': df_ssr_r, 'STR': df_str_r
    })

for sector, coeffs in coeffs.items():
    print(f"\n\nEquations for {sector} sector:")
    for month, coeff in coeffs.items():
        print(f'\n{month}:\n' + ' + '.join([f'{coeff[x]}*({x})' if x!='const' else str(coeff[x]) for x in coeff]))