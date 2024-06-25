import matplotlib.pyplot as plt
import scipy.signal as signal
import pandas as pd
import numpy as np
from scipy.stats import pearsonr

def plot_graph(ax, extent_values, extent_bfl, soi_values, soi_bfl, month):
    ax.scatter(soi_values, extent_values, color='y', alpha=0.5)
    ax.scatter(soi_bfl, extent_bfl, color='b', alpha=0.5, label='best fit')
    ax.set_title(month)

def is_leap_year(year):
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

# Butterworth Filter params
bw_order  = 1     # Filter order
bw_cfreq  = 0.4   # Cutoff frequency
B, A = signal.butter(bw_order, bw_cfreq, btype='lowpass', analog=False)

year_list = list(range(1979, 2024))
sectors = ["Bell-Amundsen", "Indian", "Pacific", "Ross", "Weddell"]
rel_path = "../../data/"

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

# ENSO Data
txt_path = rel_path + "darwin.anom_.txt"
columns = ['Year'] + list(month_days.keys())

df_soi = pd.read_csv(txt_path, delim_whitespace=True, names=columns)
df_soi = df_soi[df_soi['Year']>=1979].head(-1).reset_index()
df_soi.drop(df_soi.columns[[0,1]], axis=1, inplace=True)

# Apply butterworth filter
for month in month_days.keys():
    df_soi[month] = signal.filtfilt(B, A, df_soi[month])


for sector in sectors:
    # Sea Ice Index Data
    excel_path = rel_path + "S_Sea_Ice_Index_Regional_Daily_Data_G02135_v3.0.xlsx"
    df_sea_ice = pd.read_excel(excel_path, sheet_name = sector + "-Extent-km^2")
    df_sea_ice.drop(df_sea_ice.columns[[-1, 0, 1, 2]], axis=1, inplace=True)

    # Convert to a 1D Series, excluding February 29 in non-leap years
    extent_values = []
    for year in year_list:
        yearly_data = df_sea_ice[year].values
        if not is_leap_year(year):
            # Drop the 59th day (February 29) for non-leap years
            yearly_data = np.concatenate((yearly_data[:59], yearly_data[60:]))
        extent_values.extend(yearly_data)

    extent = pd.Series(extent_values).astype(float)
    extent.interpolate(method='linear', inplace=True)

    # Apply butterworth filter
    extent = pd.Series(signal.filtfilt(B,A, extent))

    date_range = pd.date_range(start='1979-01-01', end='2023-12-31', freq='D')
    df_daily = pd.DataFrame(extent, columns=['value'])
    df_daily.set_index(date_range, inplace=True)
    
    df_monthly = df_daily.resample('M').mean()
    df_monthly['Year'] = df_monthly.index.year
    df_monthly['Month'] = df_monthly.index.strftime('%B')

    df_pivot = df_monthly.pivot(index='Year', columns='Month', values='value')
    df_pivot = df_pivot[list(month_days.keys())]
    df_pivot.reset_index(drop=True, inplace=True)

    print('\n'+sector)
    for month in list(month_days.keys()):

        a = pearsonr(df_soi[month], df_pivot[month])
        if a[1] < 0.05: print("\033[0;32m", end='')
        print(f'{month}: {round(a[0], 3)} {round(a[1], 3)} \033[0m')

        # plt.scatter(df_soi, extent, alpha=0.8)
        # plt.title(sector)
        # plt.xlabel("SOI Index")
        # plt.ylabel("Extent data")
        # plt.show()