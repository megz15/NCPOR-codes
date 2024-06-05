import matplotlib.pyplot as plt
import pandas as pd
import scipy.signal as signal

def expand_to_daily(df):
    daily_values = []

    for _, row in df.iterrows():
        for month, days in month_days.items():
            daily_values.extend([row[month]] * days)

    return(pd.Series(daily_values))

year_list = list(range(1979, 2024))
rel_path = "../../data/"

month_days = {
    "January": 31,
    "February": 29,
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
excel_path = rel_path + "S_Sea_Ice_Index_Regional_Daily_Data_G02135_v3.0.xlsx"
df_sea_ice = pd.read_excel(excel_path, sheet_name="Bell-Amundsen-Extent-km^2")
df_sea_ice.drop(df_sea_ice.columns[[-1, 0, 1, 2]],axis=1,inplace=True)

extent = pd.Series(df_sea_ice[[year for year in year_list]].values.ravel()).astype(float)
extent.interpolate(method='linear', inplace=True)

# ENSO Data
txt_path = rel_path + "darwin.anom_.txt"
columns = ['Year'] + list(month_days.keys())

df_soi = pd.read_csv(txt_path, delim_whitespace=True, names=columns)
df_soi = df_soi[df_soi['Year']>=1979].head(-1).reset_index()
df_soi_daily = expand_to_daily(df_soi)

# Butterworth Filter
N  = 2    # Filter order
Wn = 0.6  # Cutoff frequency
B, A = signal.butter(N, Wn, output='ba')
extentf = pd.Series(signal.filtfilt(B,A, extent))
residual = extent-extentf