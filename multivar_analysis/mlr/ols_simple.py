from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import pandas as pd

years = list(range(1979, 2024))

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
    models = {}

    for month in month_list:
        for i in list(region_iv.keys()):
            iv[month][i] = region_iv[i][month]

        x = iv[month]
        y = dv[month]

        model = LinearRegression(fit_intercept = True)
        model.fit(x, y)

        models[month] = model
    return models

models = {}

for sector in list(sectors.keys()):
    df_sie_r = df_sie[df_sie['Sector'] == sector]
    df_ssr_r = df_ssr[df_ssr['Sector'] == sector].reset_index(drop=True)
    df_str_r = df_str[df_str['Sector'] == sector].reset_index(drop=True)

    df_sie_r = df_sie_r.drop(columns = ['Sector', 'Year']).reset_index(drop=True)

    models[sector] = perform_mlr(df_sie_r, iv, {
        'SSR': df_ssr_r,
        'STR': df_str_r,
    })

for sector, sector_models in models.items():
    print(f"\nEquations for {sector} sector:")
    for month, model in sector_models.items():
        print(f'{month}: {model.intercept_} + {' + '.join(
            [f'{x}*({y})' for x,y in zip(model.coef_, model.feature_names_in_)]
        )}')

for sector, sector_models in models.items():
    df_sie_r = df_sie[df_sie['Sector'] == sector].drop(columns=['Sector', 'Year']).reset_index(drop=True)

    print(f'\nSector - {sector}')
    for month in month_list:
        x = iv[month].copy()
        x['SSR'] = df_ssr[df_ssr['Sector'] == sector][month].values
        x['STR'] = df_str[df_str['Sector'] == sector][month].values
        y = df_sie_r[month]

        model = sector_models[month]
        y_pred = model.predict(x)

        print(f'{month.ljust(9)}\tR2:{str(round(r2_score(y, y_pred), 3)).ljust(5)}\tMSE:{round(mean_squared_error(y, y_pred), 3)}\tMAE:{round(mean_absolute_error(y, y_pred), 3)}')

        # print('Year\tActual\t\tPrediction\tDifference')
        # for year, x,y in zip(years, y, y_pred):
        #     print(f'{year}\t{round(x,3)}\t{round(y,3)}\t{round(y-x,3)}')