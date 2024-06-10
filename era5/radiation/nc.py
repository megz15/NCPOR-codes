import xarray as xr

# longitude ranges
regions = {
    'Ross': (160, -130),
    'Bell-Amundsen': (-130, -60),
    'Weddell': (-60, 20),
    'Indian': (20, 90),
    'Pacific': (90, 160)
}

region = 'Ross'
month  = 1 # January

rel_path = '../../data/'
file_path = rel_path + 'netcdf/rad/radiation_1979-2023_monthly_seaice.nc'

with xr.open_dataset(file_path) as ds:
    resampled_ds = ds['str'].sel(
        longitude = slice(
            min(regions[region]), max(regions[region])
        )).mean(dim=['latitude', 'longitude'])
    
    resampled_df = resampled_ds.to_dataframe().reset_index()
    
    resampled_df['Month'] = resampled_df['time'].dt.month
    resampled_df['Year'] = resampled_df['time'].dt.year
    pivot_df = resampled_df.pivot(index='Year', columns='Month', values='str').reset_index()

    print(pivot_df)