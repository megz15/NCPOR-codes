from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.linear_model import LinearRegression
import pandas as pd

# Parameters
poly_deg = 1
calc_intercept = True
rel_path = "../../data/"

sectors = {
    'Ross': {'lon': (160, -130), 'lat': (-50, -72)},
    'Bell-Amundsen': {'lon': (-130, -60), 'lat': (-50, -72)},
    'Weddell': {'lon': (-60, 20), 'lat': (-50, -72)},
    'Indian': {'lon': (20, 90), 'lat': (-50, -72)},
    'Pacific': {'lon': (90, 160), 'lat': (-50, -72)}
}

month_list = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
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

iv = {}
for month in month_list:
    iv[month] = pd.DataFrame({"ENSO": df_soi[month], "PDO": df_pdo[month], "IOD": df_iod[month]})

# Standardizing iv values
scaler = StandardScaler()

for month, df in iv.items():
    iv[month] = pd.DataFrame(scaler.fit_transform(df), columns=df.columns)

def perform_mlr(dv, iv, region_iv):
    coeffs = {}
    actual_vs_predicted = {}

    for month in month_list:
        for i in list(region_iv.keys()):
            iv[month][i] = region_iv[i][month]

        x = iv[month]
        y = dv[month]

        poly = PolynomialFeatures(degree = poly_deg, include_bias = calc_intercept)
        x_poly = poly.fit_transform(x)

        model = LinearRegression(fit_intercept = False)
        model.fit(x_poly, y)

        coeffs[month] = dict(zip(poly.get_feature_names_out().tolist(), model.coef_.tolist()))

        y_pred = model.predict(x_poly)
        actual_vs_predicted[month] = pd.DataFrame({'Actual': y, 'Predicted': y_pred})
    return coeffs, actual_vs_predicted

coeffs = {}
predictions = {}

for sector in list(sectors.keys()):
    df_sie_r = df_sie[df_sie['Sector'] == sector]
    df_ssr_r = df_ssr[df_ssr['Sector'] == sector].reset_index(drop=True)
    df_str_r = df_str[df_str['Sector'] == sector].reset_index(drop=True)

    df_sie_r = df_sie_r.drop(columns = ['Sector', 'Year']).reset_index(drop=True)

    coeffs[sector], predictions[sector] = perform_mlr(df_sie_r, iv, {
        'SSR': df_ssr_r, 'STR': df_str_r
    })

for sector, coeffs in coeffs.items():
    print(f"\n\nEquations for {sector} sector:")
    for month, coeff in coeffs.items():
        print(f'\n{month}: ' + ' + '.join([f'{coeff[x]}*({x})' for x in coeff]))

for sector in list(sectors.keys()):
    print(f"\nActual vs Predicted values for {sector} sector:")
    for month, actual_vs_predicted in predictions[sector].items():
        print(f'\n{month}:\n', actual_vs_predicted)