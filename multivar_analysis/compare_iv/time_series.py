import pandas as pd
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

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
    for name, df in df_dict.items():
        filt_df = df[(df['Date'] >= start) & (df['Date'] <= end)]
        plt.plot(filt_df['Date'], filt_df['Value'], label=name)
    plt.title(f'Sector: {sector}')
    plt.xlabel('Date')
    plt.ylabel('Standardized Value')
    plt.legend(loc='upper right')
    plt.grid(True)
    plt.show()

sectors = {
    'Ross': {'lon': (160, -130), 'lat': (-50, -72)},
    'Bell-Amundsen': {'lon': (-130, -60), 'lat': (-50, -72)},
    'Weddell': {'lon': (-60, 20), 'lat': (-50, -72)},
    'Indian': {'lon': (20, 90), 'lat': (-50, -72)},
    'Pacific': {'lon': (90, 160), 'lat': (-50, -72)}
}

months = {
    'January': '01', 'February': '02', 'March': '03', 'April': '04', 
    'May': '05', 'June': '06', 'July': '07', 'August': '08', 
    'September': '09', 'October': '10', 'November': '11', 'December': '12'
}

start = '1979-01-01'
end = '2024-01-01'

# Independent Variables (IVs)
df_soi = pd.read_pickle('pickles/soi.pkl')
df_pdo = pd.read_pickle('pickles/pdo.pkl')
df_iod = pd.read_pickle('pickles/iod.pkl')

df_ssr = pd.read_pickle('pickles/ssr.pkl')
df_str = pd.read_pickle('pickles/str.pkl')

# df_u10 = pd.read_pickle('pickles/u10.pkl')
# df_v10 = pd.read_pickle('pickles/v10.pkl')

# df_t2m = pd.read_pickle('pickles/t2m.pkl')

df_slhf = pd.ExcelFile('other_data/monthly_slhf_value_filtered.xlsx')
df_sshf = pd.ExcelFile('other_data/monthly_sshf_value_filtered.xlsx')

df_u10 = pd.ExcelFile('other_data/monthly_u10_value_filtered.xlsx')
df_v10 = pd.ExcelFile('other_data/monthly_v10_value_filtered.xlsx')

df_t2m = pd.ExcelFile('other_data/monthly_t2m_value_filtered.xlsx')

# Dependent Variable (DV)
df_sie = pd.read_pickle('pickles/sie.pkl')

df_soi_flat = standardize(flatten(df_soi))
df_pdo_flat = standardize(flatten(df_pdo))
df_iod_flat = standardize(flatten(df_iod))

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
        "SIE": df_sie_flat,

        "SOI": df_soi_flat,
        "PDO": df_pdo_flat,
        "IOD": df_iod_flat,

        "SSR": df_ssr_flat,
        "STR": df_str_flat,

        "SLHF": df_slhf_flat,
        "SSHF": df_sshf_flat,

        "U10": df_u10_flat,
        "V10": df_v10_flat,

        "T2M": df_t2m_flat
    }

    plot_sector_data(sector, df_dict, start, end)