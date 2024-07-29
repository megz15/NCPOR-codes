from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

btype = "low"

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

sectors = ['Weddell', 'Indian', 'Pacific', 'Ross', 'Bell-Amundsen']

month_list = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
]

# Independent Variables (IVs)
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

# Dependent Variable (DV)
df_sie = pd.read_pickle('pickles/sie.pkl')
# df_sie[month_list] = df_transform(df_sie[month_list])

remote_iv = {}
reanalysis_iv = {}

for month in month_list:
    remote_iv[month] = pd.DataFrame({
        'ENSO': df_soi[month], 'PDO': df_pdo[month], 'IOD': df_iod[month], 'SAM': df_sam[month]
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

contributions_dict = {kind: {var: {} for var in sectors} for kind in ("Remote", "Reanalysis")}

for sector in sectors:
    # print(f'\n\033[105mEquations for {sector} sector:\033[0m')
    
    for month, remote_model, reanalysis_model in zip(month_list, remote_models[sector].values(), reanalysis_models[sector].values()):
        # print("\033[93mMonth - " + month)

        for kind, model in zip(("Remote", "Reanalysis"), (remote_model, reanalysis_model)):
            coefficients = model.coef_
            feature_names = model.feature_names_in_
            total_abs_coefs = np.sum(np.abs(coefficients))
            contributions = {name: round(np.abs(coeff) / total_abs_coefs * 100, 3) for name, coeff in zip(feature_names, coefficients)}

            # print(f'\033[95m{kind.ljust(10)}\t' + '\t'.join(contributions.keys()) + '\033[0m')
            # print("Contributions\t" + '%\t'.join(map(str, contributions.values())) + '%')

            contributions_dict[kind][sector][month] = contributions

for sector in sectors:
    for variable in ['Remote', 'Reanalysis']:

        vars = ['ENSO', 'PDO', 'IOD', 'SAM'] if variable == "Remote" else ['SSR', 'STR', 'SLHF', 'SSHF', 'U10', 'V10', 'T2M']

        plt.figure(figsize=(13.66, 7.38), dpi=200)

        fig, axs = plt.subplots(3, 4, figsize=(13.66, 7.38), dpi=200)
        for i, month in enumerate(month_list):
            data_to_plot = [contributions_dict[variable][sector][month][var] for var in vars]
            ax = axs[i // 4, i % 4]
            wedges, texts = ax.pie(data_to_plot, startangle=90,
                # textprops={'fontsize': 12}, labels=vars,
                colors=sns.color_palette("muted")
            )

            labels=[f'{s:0.1f}%' for s in data_to_plot]
            ax.legend(wedges, labels, loc='center left', bbox_to_anchor=(1, 0.5), handlelength=0.7, handletextpad=0.2, frameon=False, prop={'weight': 'bold', 'size': 12 if variable == "Reanalysis" else 14})
            ax.set_title(month[:3], fontsize=14, weight="bold")
        fig.legend(vars, loc='lower center', handlelength=0.7, frameon=False, ncol=len(vars), prop={'weight':'bold', 'size': 12})

        # figManager = plt.get_current_fig_manager()
        # figManager.window.showMaximized()

        plt.suptitle(f"{variable} ({btype}-pass): {sector if sector!="Bell-Amundsen" else "Bellingshausen-Amundsen"} {"Ocean" if sector in ["Indian", "Pacific"] else "Sea"}", fontsize=16, weight="bold")

        fig.tight_layout()
        output_dir = f"results/percentages/{btype}/{variable}"

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        plt.savefig(os.path.join(output_dir, f'{sector}_{variable}.png'))
        plt.close()
        
        # plt.show()