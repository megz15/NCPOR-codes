import pandas as pd
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import numpy as np
import os

btype = "high"

def flatten(df, sector = None):
    if sector: df = df.drop(columns=["Sector"])
    df_flat = pd.melt(df, id_vars=['Year'], var_name='Month', value_name='Value')

    df_flat['Month'] = df_flat['Month'].map(months)
    df_flat['Date'] = pd.to_datetime(df_flat['Year'].astype(str) + '-' + df_flat['Month'] + '-01')
    
    df_flat.drop(columns=['Year', 'Month'], inplace=True)
    df_flat.sort_values(by='Date', inplace=True)
    df_flat.reset_index(drop = True, inplace=True)
    
    return df_flat

def standardize(df):
    scaler = StandardScaler()
    df['Value'] = scaler.fit_transform(df[['Value']])
    return df

def plot_sector_data(sector, df_dict, start, end):
    plt.figure(figsize=(13.66, 7.38), dpi=200)

    for name, df in df_dict.items():
        filt_df = df[(df['Date'] >= start) & (df['Date'] <= end)]
        plt.plot(filt_df['Date'], filt_df['Value'], label=name)
    plt.title(f'Sector: {sector if sector!="Bell-Amundsen" else "Bellingshausen-Amundsen"} {"Ocean" if sector in ["Indian", "Pacific"] else "Sea"}', fontsize=18, weight='bold')

    min_val = filt_df['Value'].min()
    max_val = filt_df['Value'].max()

    min_range = np.floor(min_val * 2) / 2
    max_range = np.ceil(max_val * 2) / 2

    range_values = np.arange(min_range, max_range + 0.5, 0.5)
    
    plt.xlabel('Date', fontsize=15, labelpad=10, weight='bold')
    plt.ylabel('Standardized Value', fontsize=15, labelpad=10, weight='bold')
    
    year_starts = pd.date_range(start=start, end=end, freq='YS')[::2]
    plt.xticks(year_starts, year_starts.strftime('%Y'), rotation=90, fontsize=14, weight='bold')
    plt.yticks(range_values, fontsize=14, weight='bold')
    
    plt.legend(loc='upper right', prop={'size': 14, 'weight': 'bold'}, ncol=2)
    plt.grid(True)
    plt.margins(x=0)

    # figManager = plt.get_current_fig_manager()
    # figManager.window.showMaximized()

    plt.tight_layout()

    output_dir = f"results/timeseries/{btype}/{name}"

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    plt.savefig(os.path.join(output_dir, f'{sector}.png'))
    plt.close()

    # plt.show()

sectors = {
    'Weddell': {'lon': (-60, 20), 'lat': (-50, -72)},
    'Indian': {'lon': (20, 90), 'lat': (-50, -72)},
    'Pacific': {'lon': (90, 160), 'lat': (-50, -72)},
    'Ross': {'lon': (160, -130), 'lat': (-50, -72)},
    'Bell-Amundsen': {'lon': (-130, -60), 'lat': (-50, -72)},
}

months = {
    'January': '01', 'February': '02', 'March': '03', 'April': '04', 
    'May': '05', 'June': '06', 'July': '07', 'August': '08', 
    'September': '09', 'October': '10', 'November': '11', 'December': '12'
}

start = '1979-01-01'
end = '2023-12-01'

# Independent Variables (IVs)
df_soi = pd.read_pickle('pickles/high_soi.pkl')
df_pdo = pd.read_pickle('pickles/high_pdo.pkl')
df_iod = pd.read_pickle('pickles/high_iod.pkl')

df_sam = pd.read_excel('other_data/highpass/sam_high.xlsx')

df_ssr = pd.read_pickle('pickles/high_ssr.pkl')
df_str = pd.read_pickle('pickles/high_str.pkl')

# df_u10 = pd.read_pickle('pickles/u10.pkl')
# df_v10 = pd.read_pickle('pickles/v10.pkl')

# df_t2m = pd.read_pickle('pickles/t2m.pkl')

df_slhf = pd.ExcelFile('other_data/highpass/monthly_slhf_high_filtered.xlsx')
df_sshf = pd.ExcelFile('other_data/highpass/monthly_sshf_high_filtered.xlsx')

df_u10 = pd.ExcelFile('other_data/highpass/monthly_u10_high_filtered.xlsx')
df_v10 = pd.ExcelFile('other_data/highpass/monthly_v10_high_filtered.xlsx')

df_t2m = pd.ExcelFile('other_data/highpass/monthly_t2m_high_filtered.xlsx')

# Dependent Variable (DV)
df_sie = pd.read_pickle('pickles/high_sie.pkl')

df_soi_flat = standardize(flatten(df_soi))
df_pdo_flat = standardize(flatten(df_pdo))
df_iod_flat = standardize(flatten(df_iod))
df_sam_flat = standardize(flatten(df_sam))

for sector in sectors:

    df_sie_flat = standardize(flatten(df_sie[ df_sie["Sector"] == sector ], sector))

    df_ssr_flat = standardize(flatten(df_ssr[ df_ssr["Sector"] == sector ], sector))
    df_str_flat = standardize(flatten(df_str[ df_str["Sector"] == sector ], sector))

    # df_u10_flat = standardize(flatten(df_u10[ df_u10["Sector"] == sector ], sector))
    # df_v10_flat = standardize(flatten(df_v10[ df_v10["Sector"] == sector ], sector))

    # df_t2m_flat = standardize(flatten(df_t2m[ df_t2m["Sector"] == sector ], sector))
    # df_t2m_flat['Value'] = df_t2m_flat['Value'].subtract(273.15)

    df_slhf_flat = standardize(flatten(pd.read_excel(df_slhf, f'{sector} Region')))
    df_sshf_flat = standardize(flatten(pd.read_excel(df_sshf, f'{sector} Region')))

    df_u10_flat = standardize(flatten(pd.read_excel(df_u10, f'{sector} Region')))
    df_v10_flat = standardize(flatten(pd.read_excel(df_v10, f'{sector} Region')))

    df_t2m_flat = standardize(flatten(pd.read_excel(df_t2m, f'{sector} Region')))

    df_dict = {
        "SOI": df_soi_flat,
        "PDO": df_pdo_flat,
        "IOD": df_iod_flat,
        "SAM": df_sam_flat,

        "SSR": df_ssr_flat,
        "STR": df_str_flat,

        "SLHF": df_slhf_flat,
        "SSHF": df_sshf_flat,

        "U10": df_u10_flat,
        "V10": df_v10_flat,

        "T2M": df_t2m_flat
    }

    for key, val in df_dict.items():
        plot_sector_data(sector, {
            "SIE": df_sie_flat,
            key: val,
        }, start, end)