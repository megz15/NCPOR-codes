from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.preprocessing import StandardScaler
import pandas as pd

def highlight_if_significant(flag, threshold = 0.5):
    return '\033[92m' if flag > threshold else '\033[0m'

def df_transform(df, method = "log"):
    return df.transform(method)

# Ridge/Tikhonov L2 Regularization
# 0 = OLS, no ridge regularization
alpha = 0

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
# df_sie[month_list] = df_transform(df_sie[month_list])

iv = {}
for month in month_list:
    iv[month] = pd.DataFrame({'ENSO': df_soi[month], 'PDO': df_pdo[month], 'IOD': df_iod[month]})

# Standardizing iv values
scaler = StandardScaler()

for month, df in iv.items():
    iv[month] = pd.DataFrame(scaler.fit_transform(df), columns=df.columns)

def perform_mlr(dv, iv, region_iv):
    models = {}
    performance = {}

    for month in month_list:
        for i in list(region_iv.keys()):
            iv[month][i] = region_iv[i][month]

        x = iv[month]
        y = dv[month]

        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

        model = Ridge(alpha = alpha) if alpha != 0 else LinearRegression()
        model.fit(x_train, y_train)

        y_pred_train = model.predict(x_train)
        y_pred_test = model.predict(x_test)

        performance[month] = {
            'train': {
                'R2': r2_score(y_train, y_pred_train),
                'MSE': mean_squared_error(y_train, y_pred_train),
                'MAE': mean_absolute_error(y_train, y_pred_train),
                'Actual': y_train,
                'Predicted': y_pred_train
            },
            'test': {
                'R2': r2_score(y_test, y_pred_test),
                'MSE': mean_squared_error(y_test, y_pred_test),
                'MAE': mean_absolute_error(y_test, y_pred_test),
                'Actual': y_test,
                'Predicted': y_pred_test
            }
        }

        models[month] = model
    return models, performance

models = {}
performances = {}

for sector in list(sectors.keys()):
    df_sie_r = df_sie[df_sie['Sector'] == sector]
    df_ssr_r = df_ssr[df_ssr['Sector'] == sector].reset_index(drop=True)
    df_str_r = df_str[df_str['Sector'] == sector].reset_index(drop=True)

    df_sie_r = df_sie_r.drop(columns = ['Sector', 'Year']).reset_index(drop=True)

    models[sector], performances[sector] = perform_mlr(df_sie_r, iv, {
        'SSR': df_ssr_r,
        'STR': df_str_r,
    })

# Print equations
for sector, sector_models in models.items():
    print(f'\n\033[105mEquations for {sector} sector:\033[0m')
    for month, model in sector_models.items():
        print(f'\033[93m{month}\033[0m: {model.intercept_} + {' + '.join(
            [f'{x}*\033[96m({y})\033[0m' for x,y in zip(model.coef_, model.feature_names_in_)]
        )}')

# Performance metrics
for sector, sector_performances in performances.items():
    print(f'\n\033[105mPerformance for {sector} sector:\033[0m')
    for month, metrics in sector_performances.items():
        print(f'{highlight_if_significant(metrics['train']['R2'])}Training {month.ljust(9)} R2: {metrics['train']['R2']:.3f}\tMSE: {metrics['train']['MSE']:.3f}\tMAE: {metrics['train']['MAE']:.3f}\033[0m')
        # for actual, predicted in zip(metrics['train']['Actual'], metrics['train']['Predicted']):
        #     print(f'Actual: {actual:.3f}\tPredicted: {predicted:.3f}\tDifference: {predicted-actual:.3f}')

        print(f'{highlight_if_significant(metrics['test']['R2'])} Testing {month.ljust(9)} R2: {metrics['test']['R2']:.3f}\tMSE: {metrics['test']['MSE']:.3f}\tMAE: {metrics['test']['MAE']:.3f}\033[0m')
        # for actual, predicted in zip(metrics['test']['Actual'], metrics['test']['Predicted']):
        #     print(f'Actual: {actual:.3f}\tPredicted: {predicted:.3f}\tDifference: {predicted-actual:.3f}')