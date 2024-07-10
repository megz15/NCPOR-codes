from scipy.signal import butter, filtfilt
import pandas as pd
import xarray as xr

# Butterworth Filter
bw_order  = 1     # Filter order
bw_cfreq  = 0.4   # Cut-off freq
B,A = butter(bw_order, bw_cfreq)

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
df_t2m_list = []

# IOD Data
for sector in list(sectors.keys()):

    # NetCDF Data
    nv_path = rel_path + 'netcdf/airtemp/airtemp_1979-2024_monthly.nc'

    with xr.open_dataset(nv_path) as ds:
        df_t2m = ds['t2m'].sel(
            longitude = slice(
                min(sectors[sector]['lon']), max(sectors[sector]['lon'])
            ), latitude = slice(
                max(sectors[sector]['lat']), min(sectors[sector]['lat'])
            ), time = slice(
                '1979-01-01', '2023-12-01'
            ), expver = 1).mean(dim = ['latitude', 'longitude'])
        
    df_t2m = df_t2m.to_dataframe().reset_index()
    
    df_t2m['Month'] = [month_list[x - 1] for x in df_t2m['time'].dt.month]
    df_t2m['Year'] = df_t2m['time'].dt.year
    
    df_t2m = df_t2m.pivot(index='Year', columns='Month', values='t2m')
    df_t2m = df_t2m[month_list]
    df_t2m.reset_index(inplace=True)

    # Apply butterworth filter
    for month in month_list:
        df_t2m[month] = filtfilt(B, A, df_t2m[month])

    df_t2m.insert(0, "Sector", sector)
    df_t2m_list.append(df_t2m)

df_t2m = pd.concat(df_t2m_list, ignore_index=True)

df_t2m.to_pickle('pickles/t2m.pkl')
# print(df_t2m)