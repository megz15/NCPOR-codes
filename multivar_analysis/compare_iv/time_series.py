import pandas as pd

def flatten(df, sector = None):

    if sector: df = df.drop(columns=["Sector"])

    year = 'Year'

    try:
        df_flat = pd.melt(df, id_vars=[year], var_name='Month', value_name='Value')
    except KeyError as e:
        year = 'year'
        df_flat = pd.melt(df, id_vars=[year], var_name='Month', value_name='Value')

    df_flat['Month'] = df_flat['Month'].map(months)
    df_flat['Date'] = pd.to_datetime(df_flat[year].astype(str) + '-' + df_flat['Month'] + '-01')
    
    df_flat.drop(columns=[year, 'Month'], inplace=True)
    df_flat.sort_values(by='Date', inplace=True)
    df_flat.reset_index(drop = True, inplace=True)
    
    return df_flat

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

# Independent Variables (IVs)
# Mine
df_soi = pd.read_pickle('pickles/soi.pkl')
df_pdo = pd.read_pickle('pickles/pdo.pkl')
df_iod = pd.read_pickle('pickles/iod.pkl')

df_ssr = pd.read_pickle('pickles/ssr.pkl')
df_str = pd.read_pickle('pickles/str.pkl')

df_u10 = pd.read_pickle('pickles/u10.pkl')
df_v10 = pd.read_pickle('pickles/v10.pkl')

df_t2m = pd.read_pickle('pickles/t2m.pkl')

# Others
df_slhf = pd.ExcelFile('other_data/monthly_slhf_value_filtered.xlsx')
df_sshf = pd.ExcelFile('other_data/monthly_sshf_value_filtered.xlsx')

# Dependent Variable (DV)
df_sie = pd.read_pickle('pickles/sie.pkl')

df_soi_flat = flatten(df_soi)
df_pdo_flat = flatten(df_pdo)
df_iod_flat = flatten(df_iod)

for sector in sectors:

    df_ssr_flat = flatten(df_ssr[ df_ssr["Sector"] == sector ], sector)
    df_str_flat = flatten(df_str[ df_str["Sector"] == sector ], sector)

    df_u10_flat = flatten(df_u10[ df_u10["Sector"] == sector ], sector)
    df_v10_flat = flatten(df_v10[ df_v10["Sector"] == sector ], sector)

    df_t2m_flat = flatten(df_t2m[ df_t2m["Sector"] == sector ], sector)
    df_t2m_flat['Value'] = df_t2m_flat['Value'].subtract(273.15)

    df_slhf_flat = flatten(pd.read_excel(df_slhf, f'{sector} Region'))
    df_sshf_flat = flatten(pd.read_excel(df_sshf, f'{sector} Region'))