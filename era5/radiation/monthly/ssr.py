from matplotlib import pyplot as plt
import numpy as np
import xarray as xr
import pandas as pd
from scipy.stats import pearsonr
import scipy.signal as signal

# Longitude and Latitude ranges
regions = {
    'Ross':{
        'lon': (160, -130),
        'lat': (-50, -72)
    }, 'Bell-Amundsen': {
        'lon': (-130, -60),
        'lat': (-50, -72)
    }, 'Weddell': {
        'lon': (-60, 20),
        'lat': (-50, -72)
    }, 'Indian': {
        'lon': (20, 90),
        'lat': (-50, -72)
    }, 'Pacific': {
        'lon': (90, 160),
        'lat': (-50, -72)}
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
        resampled_ds = ds['ssr'].sel(
            longitude = slice(
                min(regions[region]['lon']), max(regions[region]['lon'])
            ), latitude = slice(
                max(regions[region]['lat']), min(regions[region]['lat'])
            )).mean(dim=['latitude', 'longitude'])
        
        resampled_df = resampled_ds.to_dataframe().reset_index()
        
        resampled_df['Month'] = resampled_df['time'].dt.month
        resampled_df['Year'] = resampled_df['time'].dt.year
        
        df_nc_resampled_monthly = resampled_df.pivot(index='Year', columns='Month', values='ssr')

    fig, axes = plt.subplots(3, 4, sharex=True, sharey=True)
    axes = axes.flatten()

    print(f"\n\033[0;31m{region.ljust(10)}\t\033[0;33mCorr\tp-Value\033[0m")
    for month in month_list:

        df_sea_ice = pd.read_excel(excel_path, sheet_name = region + "-Extent-km^2").head(-1).tail(-3).reset_index()

        year = pd.Series(df_sea_ice["Unnamed: 0"]).astype(int)
        extent = pd.Series(df_sea_ice[month]).astype(float)

        extent = extent.interpolate(method='linear')
        extent = extent.transform("rank")
        df_nc_resampled_monthly = df_nc_resampled_monthly.transform("rank")

        # Best fit
        coefficients = np.polyfit(year, extent, 5)
        bfl_values = np.polyval(coefficients, year)

        curr_corr, p_value = pearsonr(extent, df_nc_resampled_monthly[month_list.index(month) + 1])
        curr_corr = round(curr_corr, 3)
        p_value = round(p_value, 3)

        print(month.ljust(10), end='\t')
        print(("\033[0;32m" if p_value < 0.05 else "") + str(curr_corr) + "\033[0m", end='\t')
        print(p_value)

        # Plotting
        ax = axes[month_list.index(month)]
        ax.plot(year, extent, label='Sea Ice Extent', color='b')
        ax.plot(year, bfl_values, label='Extent Best Fit', color='g')

        # Identifying minimas and maximas
        residuals = extent - bfl_values
        minima_indices = signal.argrelextrema(residuals.values, np.less)[0]
        maxima_indices = signal.argrelextrema(residuals.values, np.greater)[0]

        minimas = [(i, residuals.values[i]) for i in minima_indices if residuals.values[i] < 0]
        maximas = [(i, residuals.values[i]) for i in maxima_indices if residuals.values[i] > 0]

        minimas_sorted = sorted(minimas, key=lambda x: x[1])
        maximas_sorted = sorted(maximas, key=lambda x: x[1], reverse=True)

        for idx, (i, _) in enumerate(minimas_sorted):
            ax.annotate(f'A{idx+1}', xy=(year[i], extent.iloc[i]), 
                        xytext=(year[i], extent.iloc[i] - 0.1))

        for idx, (i, _) in enumerate(maximas_sorted):
            ax.annotate(f'B{idx+1}', xy=(year[i], extent.iloc[i]), 
                        xytext=(year[i], extent.iloc[i] + 0.1))

        ax.plot(df_nc_resampled_monthly.index, df_nc_resampled_monthly[month_list.index(month) + 1], label='Surface Radiation', color='r')
        ax.set_title(f"{region} - {month}")
        ax.legend()
        ax.grid(True)

    plt.show()