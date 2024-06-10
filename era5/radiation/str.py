import xarray as xr
import pandas as pd
import numpy as np
import scipy.signal as signal
from scipy.stats import pearsonr
import matplotlib.pyplot as plt

def is_leap_year(year):
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

# Butterworth Filter params
bw_order  = 1     # Filter order
bw_cfreq  = 0.4   # Cutoff frequency
B, A = signal.butter(bw_order, bw_cfreq, btype='lowpass', analog=False)

# Longitude ranges
regions = {
    'Ross': (160, -130),
    'Bell-Amundsen': (-130, -60),
    'Weddell': (-60, 20),
    'Indian': (20, 90),
    'Pacific': (90, 160)
}

rel_path = "../../data/"

year_list = list(range(1979, 2024))
month_days = {
    "January": 31,
    "February": 28,
    "March": 31,
    "April": 30,
    "May": 31,
    "June": 30,
    "July": 31,
    "August": 31,
    "September": 30,
    "October": 31,
    "November": 30,
    "December": 31
}
for region in list(regions.keys()):
    
    # Sea Ice Index Data
    excel_path = rel_path + "S_Sea_Ice_Index_Regional_Daily_Data_G02135_v3.0.xlsx"
    df_sea_ice = pd.read_excel(excel_path, sheet_name = region + "-Extent-km^2")
    df_sea_ice.drop(df_sea_ice.columns[[-1, 0, 1, 2]],axis=1,inplace=True)

    extent_values = []
    for year in year_list:
        yearly_data = df_sea_ice[year].values
        if not is_leap_year(year):
            # Drop the 59th day (February 29) for non-leap years
            yearly_data = np.concatenate((yearly_data[:59], yearly_data[60:]))
        extent_values.extend(yearly_data)

    extent = pd.Series(extent_values).astype(float)
    extent.interpolate(method='linear', inplace=True)
    extent = pd.Series(signal.filtfilt(B,A, extent))

    date_range = pd.date_range(start='1979-01-01', end='2023-12-31', freq='D')
    df_daily = pd.DataFrame(extent, columns=['value'])
    df_daily.set_index(date_range, inplace=True)

    df_monthly = df_daily.resample('M').mean()
    df_monthly['Year'] = df_monthly.index.year
    df_monthly['Month'] = df_monthly.index.month

    df_extent_resampled_monthly = df_monthly.pivot(index='Year', columns='Month', values='value')

    # NetCDF Data
    nv_path = rel_path + 'netcdf/rad/radiation_1979-2023_monthly_seaice.nc'

    with xr.open_dataset(nv_path) as ds:
        resampled_ds = ds['str'].sel(
            longitude = slice(
                min(regions[region]), max(regions[region])
            )).mean(dim=['latitude', 'longitude'])
        
        resampled_df = resampled_ds.to_dataframe().reset_index()
        
        resampled_df['Month'] = resampled_df['time'].dt.month
        resampled_df['Year'] = resampled_df['time'].dt.year
        
        df_nc_resampled_monthly = resampled_df.pivot(index='Year', columns='Month', values='str')

    fig, axes = plt.subplots(3, 4)
    axes = axes.flatten()

    print(f"\n\033[0;31m{region.ljust(10)}\t\033[0;33mCorr\tp-Value\033[0m")
    for month in list(range(len(month_days))):

        curr_corr, p_value = pearsonr(df_extent_resampled_monthly[month + 1], df_nc_resampled_monthly[month + 1])
        curr_corr = round(curr_corr, 3)
        p_value = round(p_value, 3)

        print(list(month_days.keys())[month].ljust(10), end='\t')
        print(("\033[0;32m" if p_value < 0.05 else "") + str(curr_corr) + "\033[0m", end='\t')
        print(p_value)

        # Plotting
        ax = axes[month]
        ax.plot(df_extent_resampled_monthly.index, df_extent_resampled_monthly[month + 1], label='Sea Ice Extent', color='b')
        ax.plot(df_nc_resampled_monthly.index, df_nc_resampled_monthly[month + 1], label='Surface Radiation', color='r')
        ax.set_title(f"{region} - {list(month_days.keys())[month]}")
        ax.legend()
        ax.grid(True)

    # plt.tight_layout()
    plt.show()