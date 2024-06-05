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
    N  = 2    # Filter order
    Wn = 0.6  # Cutoff frequency
    B, A = signal.butter(N, Wn, output='ba')
    extentf = pd.Series(signal.filtfilt(B,A, extent))

    # Reshape to monthly data by averaging daily values
    monthly_data = {}
    for year in year_list:
        monthly_data[year] = {}
        for month, days in month_days.items():
            start_index = (pd.to_datetime(f"{year}-{month}-01")).dayofyear - 1
            end_index = start_index + days - 1
            monthly_data[year][month] = extentf.iloc[start_index:end_index].mean()

    # Convert monthly_data dictionary to DataFrame (optional)
    df_sea_ice_filt_daily_avg = pd.DataFrame.from_dict(monthly_data, orient="index", columns=month_days.keys()).reset_index()

    # print(f"\n\033[0;31m{region.ljust(10)}\t\033[0;33mCorr\033[0m")
    # for month in list(month_days.keys()):

    #     curr_corr = round(df_sea_ice_filt_daily_avg[month].corr(df_soi[month], method="pearson"), 3)

    #     print(month.ljust(10), end='\t')
    #     print(("\033[0;32m" if abs(curr_corr) > pearson_threshold else "") + str(curr_corr) + "\033[0m")