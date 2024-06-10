import pandas as pd
import numpy as np
import scipy.signal as signal
from scipy.stats import pearsonr

def is_leap_year(year): return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

# Butterworth Filter params
bw_order  = 1     # Filter order
bw_cfreq  = 0.4   # Cutoff frequency
B, A = signal.butter(bw_order, bw_cfreq, btype='lowpass', analog=False)

year_list = list(range(1979, 2024))
regions = ["Bell-Amundsen", "Indian", "Pacific", "Ross", "Weddell"]
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

# Sea Ice Index Data
# excel_path = rel_path + "S_Sea_Ice_Index_Regional_Daily_Data_G02135_v3.0.xlsx"
# df_sea_ice = pd.read_excel(excel_path, sheet_name = regions[0] + "-Extent-km^2")
# df_sea_ice.drop(df_sea_ice.columns[[-1, 0, 1, 2]],axis=1,inplace=True)

# extent_values = []
# for year in year_list:
#     yearly_data = df_sea_ice[year].values
#     if not is_leap_year(year):
#         # Drop the 59th day (February 29) for non-leap years
#         yearly_data = np.concatenate((yearly_data[:59], yearly_data[60:]))
#     extent_values.extend(yearly_data)

# extent = pd.Series(extent_values).astype(float)
# extent.interpolate(method='linear', inplace=True)
# extent = pd.Series(signal.filtfilt(B,A, extent))

# date_range = pd.date_range(start='1979-01-01', end='2023-12-31', freq='D')
# df_daily = pd.DataFrame(extent, columns=['value'])
# df_daily.set_index(date_range, inplace=True)

# df_monthly = df_daily.resample('M').mean()
# df_monthly['Year'] = df_monthly.index.year
# df_monthly['Month'] = df_monthly.index.strftime('%B')

# df_resampled_monthly = df_monthly.pivot(index='Year', columns='Month', values='value')
# df_resampled_monthly = df_resampled_monthly[list(month_days.keys())]
# df_resampled_monthly.reset_index(drop=True, inplace=True)