import xarray as xr
import pandas as pd
import numpy as np
import scipy.signal as signal
from scipy.stats import pearsonr
import matplotlib.pyplot as plt

# Longitude and Latitude ranges
regions = {
    'Ross': {'lon': (160, -130), 'lat': (-50, -72)},
    'Bell-Amundsen': {'lon': (-130, -60), 'lat': (-50, -72)},
    'Weddell': {'lon': (-60, 20), 'lat': (-50, -72)},
    'Indian': {'lon': (20, 90), 'lat': (-50, -72)},
    'Pacific': {'lon': (90, 160), 'lat': (-50, -72)}
}

rel_path = "../../data/"

year_list = list(range(1979, 2024))
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

excel_path = rel_path + "S_Sea_Ice_Index_Regional_Monthly_Data_G02135_v3.0.xlsx"

for region in list(regions.keys()):

    # NetCDF Data
    nv_path = rel_path + 'netcdf/rad/radiation_1979-2023_monthly_seaice.nc'

    with xr.open_dataset(nv_path) as ds:
        resampled_ds = ds['str'].sel(
            longitude = slice(
                min(regions[region]['lon']), max(regions[region]['lon'])
            ), latitude = slice(
                max(regions[region]['lat']), min(regions[region]['lat'])
            )).mean(dim=['latitude', 'longitude'])
        
        resampled_df = resampled_ds.to_dataframe().reset_index()
        
        resampled_df['Month'] = resampled_df['time'].dt.month
        resampled_df['Year'] = resampled_df['time'].dt.year
        
        df_nc_resampled_monthly = resampled_df.pivot(index='Year', columns='Month', values='str')

    print(f"\n\033[0;31m{region.ljust(10)}\t\033[0;33mCorr\tp-Value\033[0m")
    for month in month_list:

        df_sea_ice = pd.read_excel(excel_path, sheet_name = region + "-Extent-km^2").head(-1).tail(-3).reset_index()

        year = pd.Series(df_sea_ice["Unnamed: 0"]).astype(int)
        extent = pd.Series(df_sea_ice[month]).astype(float)

        extent = extent.interpolate(method='linear')
        # extent = extent.transform("rank")

        curr_corr, p_value = pearsonr(extent, df_nc_resampled_monthly[month_list.index(month) + 1])
        curr_corr = round(curr_corr, 3)
        p_value = round(p_value, 3)

        print(month.ljust(10), end='\t')
        print(("\033[0;32m" if p_value < 0.05 else "") + str(curr_corr) + "\033[0m", end='\t')
        print(p_value)