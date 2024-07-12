from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
import pandas as pd

def highlight_if_significant(flag, threshold = 0.5):
    return '\033[92m' if flag > threshold else '\033[0m'

def df_transform(df, method = "log"):
    return df.transform(method)

def perform_mlr(dv, iv, region_iv):
    models = {}

    # Standardizing iv values
    scaler = StandardScaler()

    for month in month_list:
        for region in region_iv:
            iv[month][region] = region_iv[region][month]

        iv[month] = pd.DataFrame(scaler.fit_transform(iv[month]), columns=iv[month].columns)

        x = iv[month]
        y = dv[month]

        model = LinearRegression()
        model.fit(x, y)

        models[month] = model
    return models

years = range(1979, 2024)

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

iv = {}
for month in month_list:
    iv[month] = pd.DataFrame({
        'ENSO': df_soi[month], 'PDO': df_pdo[month], 'IOD': df_iod[month],
    })

models = {}

for sector in sectors:
    df_sie_r = df_sie[df_sie['Sector'] == sector]
    
    df_ssr_r = df_ssr[df_ssr['Sector'] == sector].reset_index(drop=True)
    df_str_r = df_str[df_str['Sector'] == sector].reset_index(drop=True)
    
    df_slhf_r = pd.read_excel(df_slhf, f'{sector} Region')
    df_sshf_r = pd.read_excel(df_sshf, f'{sector} Region')

    df_u10_r = pd.read_excel(df_u10, f'{sector} Region')
    df_v10_r = pd.read_excel(df_v10, f'{sector} Region')

    df_t2m_r = pd.read_excel(df_t2m, f'{sector} Region')

    df_sie_r = df_sie_r.drop(columns = ['Sector', 'Year']).reset_index(drop=True)

    models[sector] = perform_mlr(df_sie_r, iv, {
        'SSR': df_ssr_r,
        'STR': df_str_r,
        'SLHF': df_slhf_r,
        'SSHF': df_sshf_r,
        'U10': df_u10_r,
        'V10': df_v10_r,
        'T2M': df_t2m_r,
    })

for sector, sector_models in models.items():
    print(f'\n\033[105mEquations for {sector} sector:\033[0m')
    for month, model in sector_models.items():
        coefficients = model.coef_
        feature_names = model.feature_names_in_

        total_abs_coefs = sum(abs(coeff) for coeff in coefficients)
        contributions = {name: round(abs(coeff) / total_abs_coefs * 100, 3) for name, coeff in zip(feature_names, coefficients)}

        print("\033[93m" + month.ljust(10) + '\t\033[95m' + '\t'.join(contributions.keys()) + '\033[0m')
        print("Contribution\t" + '%\t'.join(map(str, contributions.values())) + '%')