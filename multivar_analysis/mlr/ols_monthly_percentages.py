from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
import pandas as pd
import numpy as np

def df_transform(df, method = "log"):
    return df.transform(method)

def perform_mlr(dv, iv):
    models = {}
    scaler = StandardScaler()

    for month in month_list:
        iv[month] = pd.DataFrame(scaler.fit_transform(iv[month]), columns=iv[month].columns)
        x, y = iv[month], dv[month]

        model = LinearRegression()
        model.fit(x, y)
        models[month] = model

    return models

sectors = ['Ross', 'Bell-Amundsen', 'Weddell', 'Indian', 'Pacific']

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

df_slhf = pd.ExcelFile('other_data/monthly_slhf_value_filtered.xlsx')
df_sshf = pd.ExcelFile('other_data/monthly_sshf_value_filtered.xlsx')

df_u10 = pd.ExcelFile('other_data/monthly_u10_value_filtered.xlsx')
df_v10 = pd.ExcelFile('other_data/monthly_v10_value_filtered.xlsx')

df_t2m = pd.ExcelFile('other_data/monthly_t2m_value_filtered.xlsx')

# Dependent Variable (DV)
df_sie = pd.read_pickle('pickles/sie.pkl')
df_sie[month_list] = df_transform(df_sie[month_list])

remote_iv = {}
reanalysis_iv = {}

for month in month_list:
    remote_iv[month] = pd.DataFrame({
        'ENSO': df_soi[month], 'PDO': df_pdo[month], 'IOD': df_iod[month],
    })

remote_models = {}
reanalysis_models = {}

for sector in sectors:
    df_sie_r = df_sie[df_sie['Sector'] == sector]

    remote_models[sector] = perform_mlr(df_sie_r, remote_iv)

    # Reanalysis data
    df_ssr_r = df_ssr[df_ssr['Sector'] == sector].reset_index(drop=True)
    df_str_r = df_str[df_str['Sector'] == sector].reset_index(drop=True)
    
    df_slhf_r = pd.read_excel(df_slhf, f'{sector} Region')
    df_sshf_r = pd.read_excel(df_sshf, f'{sector} Region')

    df_u10_r = pd.read_excel(df_u10, f'{sector} Region')
    df_v10_r = pd.read_excel(df_v10, f'{sector} Region')

    df_t2m_r = pd.read_excel(df_t2m, f'{sector} Region')
    df_t2m_r = df_t2m_r[(df_t2m_r['Year'] >= 1979) & (df_t2m_r['Year'] <= 2023)]

    df_sie_r = df_sie_r.drop(columns = ['Sector', 'Year']).reset_index(drop=True)

    for month in month_list:
        reanalysis_iv[month] = pd.DataFrame({
        'SSR': df_ssr_r[month],
        'STR': df_str_r[month],
        'SLHF': df_slhf_r[month],
        'SSHF': df_sshf_r[month],
        'U10': df_u10_r[month],
        'V10': df_v10_r[month],
        'T2M': df_t2m_r[month],
    })

    reanalysis_models[sector] = perform_mlr(df_sie_r, reanalysis_iv)

for sector, remote_models, reanalysis_models in zip(sectors, remote_models.values(), reanalysis_models.values()):
    print(f'\n\033[105mEquations for {sector} sector:\033[0m')
    
    for month, remote_model, reanalysis_model in zip(month_list, remote_models.values(), reanalysis_models.values()):

        print("\033[93mMonth - " + month)
        for kind, model in zip(("Remote", "Reanalysis"), (remote_model, reanalysis_model)):
            coefficients = model.coef_
            feature_names = model.feature_names_in_

            total_abs_coefs = np.sum(np.abs(coefficients))
            contributions = {name: round(np.abs(coeff) / total_abs_coefs * 100, 3) for name, coeff in zip(feature_names, coefficients)}

            print(f'\033[95m{kind.ljust(10)}\t' + '\t'.join(contributions.keys()) + '\033[0m')
            print("Contributions\t" + '%\t'.join(map(str, contributions.values())) + '%')