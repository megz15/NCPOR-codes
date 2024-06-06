import pandas as pd
import numpy as np
import scipy.signal as signal

def is_leap_year(year): return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

year_list = list(range(1979, 2024))
regions = ["Bell-Amundsen", "Indian", "Pacific", "Ross", "Weddell"]
rel_path = "../../data/"
pearson_threshold = 0.3
corr_values = []

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

for region in regions:
    # Sea Ice Index Data
    excel_path = rel_path + "S_Sea_Ice_Index_Regional_Daily_Data_G02135_v3.0.xlsx"
    df_sea_ice = pd.read_excel(excel_path, sheet_name = region + "-Extent-km^2")
    df_sea_ice.drop(df_sea_ice.columns[[-1, 0, 1, 2]],axis=1,inplace=True)

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

    # Butterworth Filter
    N  = 3    # Filter order
    Wn = 0.1  # Cutoff frequency
    B, A = signal.butter(N, Wn, btype='lowpass', analog=False)
    extentf = pd.Series(signal.filtfilt(B,A, extent))

    date_range = pd.date_range(start='1979-01-01', end='2023-12-31', freq='D')
    df_daily = pd.DataFrame(extentf, columns=['value'])
    df_daily.set_index(date_range, inplace=True)
    
    df_monthly = df_daily.resample('M').mean()
    df_monthly['Year'] = df_monthly.index.year
    df_monthly['Month'] = df_monthly.index.strftime('%B')

    # Pivot the DataFrame to have months as columns and years as rows
    df_pivot = df_monthly.pivot(index='Year', columns='Month', values='value')

    # Reorder the columns to have months in calendar order
    df_pivot = df_pivot[list(month_days.keys())]

    # Reset the index to get rid of the year index
    df_pivot.reset_index(drop=True, inplace=True)

    print(f"\n\033[0;31m{region.ljust(10)}\t\033[0;33mCorr\033[0m")
    for month in list(month_days.keys()):

        curr_corr = round(df_pivot[month].corr(df_soi[month], method="pearson"), 3)

        print(month.ljust(10), end='\t')
        print(("\033[0;32m" if abs(curr_corr) > pearson_threshold else "") + str(curr_corr) + "\033[0m")