from scipy.signal import butter, filtfilt
import pandas as pd
import xarray as xr

# Butterworth Filter
bw_order  = 1     # Filter order
bw_cfreq  = 0.4   # Cut-off freq
B,A = butter(bw_order, bw_cfreq, btype="high")

month_list = [
    'January',
    'February',
    'March',
    'April',
    'May',
    'June',
    'July',
    'August',
    'September',
    'October',
    'November',
    'December'
]

sectors = {
    'Ross': {'lon': (160, -130),'lat': (-50, -72)},
    'Bell-Amundsen': {'lon': (-130, -60),'lat': (-50, -72)},
    'Weddell': {'lon': (-60, 20),'lat': (-50, -72)},
    'Indian': {'lon': (20, 90),'lat': (-50, -72)},
    'Pacific': {'lon': (90, 160),'lat': (-50, -72)}
}

rel_path = "../../data/"
columns = ['Year'] + month_list
df_u10_list = []

# IOD Data
for sector in list(sectors.keys()):

    # NetCDF Data
    nv_path = rel_path + 'netcdf/wind/wind_uv10_1979-2024_monthly.nc'

    with xr.open_dataset(nv_path) as ds:
        df_u10 = ds['u10'].sel(
            longitude = slice(
                min(sectors[sector]['lon']), max(sectors[sector]['lon'])
            ), latitude = slice(
                max(sectors[sector]['lat']), min(sectors[sector]['lat'])
            ), time = slice(
                '1979-01-01', '2023-12-01'
            ), expver = 1).mean(dim = ['latitude', 'longitude'])
        
    df_u10 = df_u10.to_dataframe().reset_index()
    
    df_u10['Month'] = [month_list[x - 1] for x in df_u10['time'].dt.month]
    df_u10['Year'] = df_u10['time'].dt.year
    
    df_u10 = df_u10.pivot(index='Year', columns='Month', values='u10')
    df_u10 = df_u10[month_list]
    df_u10.reset_index(inplace=True)

    # Apply butterworth filter
    for month in month_list:
        df_u10[month] = filtfilt(B, A, df_u10[month])

    df_u10.insert(0, "Sector", sector)
    df_u10_list.append(df_u10)

df_u10 = pd.concat(df_u10_list, ignore_index=True)

df_u10.to_pickle('pickles/high_u10.pkl')
# print(df_u10)