from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
import pandas as pd
import numpy as np

start = '1979-01-01'
end = '2023-12-01'

def highlight_if_significant(flag, threshold = 20):
    return '\033[92m' if flag > threshold else '\033[0m'

def standardize(df):
    scaler = StandardScaler()
    df['Value'] = scaler.fit_transform(df[['Value']])
    return df

def flatten(df, sector = None, start = start, end = end):
    if sector: df = df.drop(columns=["Sector"])
    df_flat = pd.melt(df, id_vars=['Year'], var_name='Month', value_name='Value')

    df_flat['Month'] = df_flat['Month'].map(months)
    df_flat['Date'] = pd.to_datetime(df_flat['Year'].astype(str) + '-' + df_flat['Month'] + '-01')
    
    df_flat.drop(columns=['Year', 'Month'], inplace=True)

    df_flat = df_flat[(df_flat['Date'] >= start) & (df_flat['Date'] <= end)]

    df_flat.sort_values(by='Date', inplace=True)
    df_flat.reset_index(drop = True, inplace=True)
    
    return df_flat

sectors = ['Ross', 'Bell-Amundsen', 'Weddell', 'Indian', 'Pacific']

months = {
    'January': '01', 'February': '02', 'March': '03', 'April': '04', 
    'May': '05', 'June': '06', 'July': '07', 'August': '08', 
    'September': '09', 'October': '10', 'November': '11', 'December': '12'
}

# Dependent Variable
df_sie = pd.read_pickle('pickles/sie.pkl')

# Independent Variables
df_soi = pd.read_pickle('pickles/soi.pkl')
df_pdo = pd.read_pickle('pickles/pdo.pkl')
df_iod = pd.read_pickle('pickles/iod.pkl')

df_ssr = pd.read_pickle('pickles/ssr.pkl')
df_str = pd.read_pickle('pickles/str.pkl')

df_slhf = pd.ExcelFile('other_data/monthly_slhf_value_filtered.xlsx')
df_sshf = pd.ExcelFile('other_data/monthly_sshf_value_filtered.xlsx')

df_u10 = pd.ExcelFile('other_data/monthly_u10_value_filtered.xlsx')
df_v10 = pd.ExcelFile('other_data/monthly_v10_value_filtered.xlsx')

df_t2m = pd.ExcelFile('other_data/monthly_t2m_value_filtered.xlsx')

df_soi_flat = standardize(flatten(df_soi))
df_pdo_flat = standardize(flatten(df_pdo))
df_iod_flat = standardize(flatten(df_iod))

for sector in sectors:
    df_sie_flat = flatten(df_sie[ df_sie["Sector"] == sector ], sector)
    df_sie_flat["Value"] = df_sie_flat["Value"].transform("log")

    df_ssr_flat = standardize(flatten(df_ssr[ df_ssr["Sector"] == sector ], sector))
    df_str_flat = standardize(flatten(df_str[ df_str["Sector"] == sector ], sector))

    df_slhf_flat = standardize(flatten(pd.read_excel(df_slhf, f'{sector} Region')))
    df_sshf_flat = standardize(flatten(pd.read_excel(df_sshf, f'{sector} Region')))

    df_u10_flat = standardize(flatten(pd.read_excel(df_u10, f'{sector} Region')))
    df_v10_flat = standardize(flatten(pd.read_excel(df_v10, f'{sector} Region')))

    df_t2m_flat = standardize(flatten(pd.read_excel(df_t2m, f'{sector} Region')))

    df_merged = df_sie_flat.merge(df_ssr_flat, on='Date', suffixes=('_SIE', '_SSR'))
    df_merged = df_merged.merge(df_str_flat, on='Date', suffixes=('', '_STR'))
    df_merged = df_merged.merge(df_slhf_flat, on='Date', suffixes=('', '_SLHF'))
    df_merged = df_merged.merge(df_sshf_flat, on='Date', suffixes=('', '_SSHF'))
    df_merged = df_merged.merge(df_u10_flat, on='Date', suffixes=('', '_U10'))
    df_merged = df_merged.merge(df_v10_flat, on='Date', suffixes=('', '_V10'))
    df_merged = df_merged.merge(df_t2m_flat, on='Date', suffixes=('', '_T2M'))
    df_merged = df_merged.merge(df_soi_flat, on='Date', suffixes=('', '_SOI'))
    df_merged = df_merged.merge(df_pdo_flat, on='Date', suffixes=('', '_PDO'))
    df_merged = df_merged.merge(df_iod_flat, on='Date', suffixes=('', '_IOD'))

    x = df_merged.drop(columns=['Date', 'Value_SIE']).values
    y = df_merged['Value_SIE'].values

    model = LinearRegression()
    model.fit(x, y)

    y_pred = model.predict(x)

    perf = {
        'R2': r2_score(y, y_pred),
        'MSE': mean_squared_error(y, y_pred),
        'MAE': mean_absolute_error(y, y_pred),
        'Actual': y,
        'Predicted': y_pred
    }

    coefficients = model.coef_
    intercept = model.intercept_

    contribution = np.abs(coefficients) / np.sum(np.abs(coefficients)) * 100

    print(f'\033[91m{sector.ljust(15)} R2: {perf["R2"]:.3f}\tMSE: {perf["MSE"]:.3f}\tMAE: {perf["MAE"]:.3f}\033[0m')

    variable_names = ["STR" if x == "Value" else x[6:] for x in df_merged.drop(columns=['Date', 'Value_SIE']).columns]

    print(f'Intercept\t{intercept}')
    for var, coef, contrib in zip(variable_names, coefficients, contribution):
        print(f'{highlight_if_significant(contrib, 10)}{var.ljust(9)}\tCoefficient: {coef:.4f}\tContribution: {contrib:.3f}%')
    print()