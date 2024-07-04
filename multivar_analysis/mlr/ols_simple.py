from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.model_selection import train_test_split
import pandas as pd

def highlight_if_significant(flag, threshold = 0.5):
    return '\033[92m' if flag > threshold else '\033[0m'

def df_transform(df, method = "log"):
    return df.transform(method)

def add_polynomial_features(iv, degree=2):
    poly = PolynomialFeatures(degree, include_bias=False)
    iv_poly = {}
    for month in month_list:
        iv_poly[month] = pd.DataFrame(poly.fit_transform(iv[month]), columns=poly.get_feature_names_out(iv[month].columns))
    return iv_poly

def perform_mlr(dv, iv, region_iv):
    models = {}
    performance = {}

    # Standardizing iv values
    scaler = StandardScaler()

    for month in month_list:
        for i in list(region_iv.keys()):
            iv[month][i] = region_iv[i][month]

        x = iv[month]
        y = dv[month]

        x_standardized = pd.DataFrame(scaler.fit_transform(x), columns=x.columns)
        # y_standardized = pd.DataFrame(scaler.fit_transform(y.values.reshape(-1, 1)))[0]

        x_train, x_test, y_train, y_test = train_test_split(x_standardized, y, test_size=0.2, random_state=42)

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

models = {}
performances = {}

iv_poly = add_polynomial_features(iv, degree=1)

for sector in list(sectors.keys()):
    df_sie_r = df_sie[df_sie['Sector'] == sector]
    df_ssr_r = df_ssr[df_ssr['Sector'] == sector].reset_index(drop=True)
    df_str_r = df_str[df_str['Sector'] == sector].reset_index(drop=True)

    df_sie_r = df_sie_r.drop(columns = ['Sector', 'Year']).reset_index(drop=True)

    models[sector], performances[sector] = perform_mlr(df_sie_r, iv_poly, {
        'SSR': df_ssr_r,
        'STR': df_str_r,
    })

# Print equations
for sector, sector_models in models.items():
    print(f'\n\033[105mEquations for {sector} sector:\033[0m')
    for month, model in sector_models.items():
        coefficients = model.coef_
        feature_names = model.feature_names_in_

        total_abs_coefs = sum(abs(coeff) for coeff in coefficients)
        contributions = {name: round(abs(coeff) / total_abs_coefs * 100, 3) for name, coeff in zip(feature_names, coefficients)}

        print(f'\033[93m{month}\033[0m: {round(model.intercept_, 3)} + {' + '.join(
            [f'{round(x, 3)}*\033[96m({y})\033[0m' for x,y in zip(coefficients, feature_names)]
        )}')

        print('\033[95m' + '\t'.join(contributions.keys()) + '\033[0m')
        print('%\t'.join(map(str, contributions.values())) + '%')

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