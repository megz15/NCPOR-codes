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
df_str_list = []

# IOD Data
for sector in list(sectors.keys()):

    # NetCDF Data
    nv_path = rel_path + 'netcdf/rad/radiation_1979-2023_monthly_seaice.nc'

    with xr.open_dataset(nv_path) as ds:
        df_str = ds['str'].sel(
            longitude = slice(
                min(sectors[sector]['lon']), max(sectors[sector]['lon'])
            ), latitude = slice(
                max(sectors[sector]['lat']), min(sectors[sector]['lat'])
            )).mean(dim=['latitude', 'longitude'])
        
    df_str = df_str.to_dataframe().reset_index()
    
    df_str['Month'] = [month_list[x - 1] for x in df_str['time'].dt.month]
    df_str['Year'] = df_str['time'].dt.year
    
    df_str = df_str.pivot(index='Year', columns='Month', values='str')
    df_str = df_str[month_list]
    df_str.reset_index(inplace=True)

    # Apply butterworth filter
    for month in month_list:
        df_str[month] = filtfilt(B, A, df_str[month])

    df_str.insert(0, "Sector", sector)
    df_str_list.append(df_str)

df_str = pd.concat(df_str_list, ignore_index=True)

df_str.to_pickle('pickles/high_str.pkl')
# print(df_str)