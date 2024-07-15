from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from statsmodels.stats.outliers_influence import variance_inflation_factor
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

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

df_sam = pd.read_excel('other_data/sam.xlsx')

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
df_sam_flat = standardize(flatten(df_sam))

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

    df_reanalysis_merged = df_sie_flat.merge(df_ssr_flat, on='Date', suffixes=('_SIE', '_SSR'))
    df_reanalysis_merged = df_reanalysis_merged.merge(df_str_flat, on='Date', suffixes=('', '_STR'))
    df_reanalysis_merged = df_reanalysis_merged.merge(df_slhf_flat, on='Date', suffixes=('', '_SLHF'))
    df_reanalysis_merged = df_reanalysis_merged.merge(df_sshf_flat, on='Date', suffixes=('', '_SSHF'))
    df_reanalysis_merged = df_reanalysis_merged.merge(df_u10_flat, on='Date', suffixes=('', '_U10'))
    df_reanalysis_merged = df_reanalysis_merged.merge(df_v10_flat, on='Date', suffixes=('', '_V10'))
    df_reanalysis_merged = df_reanalysis_merged.merge(df_t2m_flat, on='Date', suffixes=('', '_T2M'))

    df_remote_merged = df_sie_flat.merge(df_soi_flat, on='Date', suffixes=('_SIE', '_SOI'))
    df_remote_merged = df_remote_merged.merge(df_pdo_flat, on='Date', suffixes=('', '_PDO'))
    df_remote_merged = df_remote_merged.merge(df_iod_flat, on='Date', suffixes=('', '_IOD'))
    df_remote_merged = df_remote_merged.merge(df_sam_flat, on='Date', suffixes=('', '_SAM'))

    # for typ, val, df_merged in zip(["Remote", "Reanalysis"], ["PDO", "STR"], [df_remote_merged, df_reanalysis_merged]):

    x_reanalysis = df_reanalysis_merged.drop(columns=['Date', 'Value_SIE']).values
    y_reanalysis = df_reanalysis_merged['Value_SIE'].values

    x_remote = df_remote_merged.drop(columns=['Date', 'Value_SIE']).values
    y_remote = df_remote_merged['Value_SIE'].values

    model_reanalysis = LinearRegression()
    model_reanalysis.fit(x_reanalysis, y_reanalysis)

    model_remote = LinearRegression()
    model_remote.fit(x_remote, y_remote)

    y_pred_reanalysis = model_reanalysis.predict(x_reanalysis)
    y_pred_remote = model_remote.predict(x_remote)

    perf_reanalysis = {
        'R2': r2_score(y_reanalysis, y_pred_reanalysis),
        'MSE': mean_squared_error(y_reanalysis, y_pred_reanalysis),
        'MAE': mean_absolute_error(y_reanalysis, y_pred_reanalysis),
        'Actual': y_reanalysis,
        'Predicted': y_pred_reanalysis
    }

    perf_remote = {
        'R2': r2_score(y_remote, y_pred_remote),
        'MSE': mean_squared_error(y_remote, y_pred_remote),
        'MAE': mean_absolute_error(y_remote, y_pred_remote),
        'Actual': y_remote,
        'Predicted': y_pred_remote
    }

    coefficients_reanalysis = model_reanalysis.coef_
    intercept_reanalysis = model_reanalysis.intercept_
    
    coefficients_remote = model_remote.coef_
    intercept_remote = model_remote.intercept_

    contribution_reanalysis = np.abs(coefficients_reanalysis) / np.sum(np.abs(coefficients_reanalysis)) * 100
    contribution_remote = np.abs(coefficients_remote) / np.sum(np.abs(coefficients_remote)) * 100

    print(f'\033[91m{sector} / Local\tR2: {perf_reanalysis["R2"]:.3f}\tMSE: {perf_reanalysis["MSE"]:.3f}\tMAE: {perf_reanalysis["MAE"]:.3f}\033[0m')
    print(f'\033[91m{sector} / Remote\tR2: {perf_remote["R2"]:.3f}\tMSE: {perf_remote["MSE"]:.3f}\tMAE: {perf_remote["MAE"]:.3f}\033[0m')

    variable_names_reanalysis = ["STR" if x == "Value" else x[6:] for x in df_reanalysis_merged.drop(columns=['Date', 'Value_SIE']).columns]
    variable_names_remote = ["PDO" if x == "Value" else x[6:] for x in df_remote_merged.drop(columns=['Date', 'Value_SIE']).columns]

    vif_data_reanalysis = [variance_inflation_factor(df_reanalysis_merged.drop(columns=['Date', 'Value_SIE']).values, i) for i in range(len(variable_names_reanalysis))]
    vif_data_remote = [variance_inflation_factor(df_remote_merged.drop(columns=['Date', 'Value_SIE']).values, i) for i in range(len(variable_names_remote))]

    print(f'{intercept_reanalysis:.3f}\t\033[100mCoeff\tLocal\tVIF\033[0m')
    for var, coef, contrib, vif in zip(variable_names_reanalysis, coefficients_reanalysis, contribution_reanalysis, vif_data_reanalysis):
        print(f'{highlight_if_significant(contrib, 10)}{var}\t{coef:.3f}\t{contrib:.3f}%\t{vif:.3f}')

    print(f'\t\033[100mCoeff\tRemote\tVIF\033[0m')
    for var, coef, contrib, vif in zip(variable_names_remote, coefficients_remote, contribution_remote, vif_data_remote):
        print(f'{highlight_if_significant(contrib, 10)}{var}\t{coef:.3f}\t{contrib:.3f}%\t{vif:.3f}')

    fig, axs = plt.subplots(1, 2)
    
    axs[0].pie(contribution_reanalysis, labels=variable_names_reanalysis, autopct='%1.1f%%', startangle=90, textprops={'fontsize': 12}, explode = [0.005] * len(variable_names_reanalysis), colors=sns.color_palette("muted"))
    axs[0].set_title('Reanalysis Variables')
    
    axs[1].pie(contribution_remote, labels=variable_names_remote, autopct='%1.1f%%', startangle=90, textprops={'fontsize': 12}, explode = [0.005] * len(variable_names_remote), colors=sns.color_palette("muted"))
    axs[1].set_title('Remote Variables')
    
    plt.rcParams.update({'font.size': 14, 'font.family': 'Arial'})
    plt.suptitle(f'{sector} - Contribution of Variables')

    figManager = plt.get_current_fig_manager()
    figManager.window.showMaximized()

    plt.tight_layout()
    plt.show()