from scipy.signal import butter, filtfilt
import pandas as pd

# Butterworth Filter
bw_order  = 1     # Filter order
bw_cfreq  = 0.4   # Cut-off freq
B,A = butter(bw_order, bw_cfreq)

sectors = ["Bell-Amundsen", "Indian", "Pacific", "Ross", "Weddell"]
rel_path = "../../data/"

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

df_sie_list = []

for sector in sectors:
    dataset_path = rel_path + "S_Sea_Ice_Index_Regional_Monthly_Data_G02135_v3.0.xlsx"

    df_sie = pd.read_excel(dataset_path, sheet_name = sector + "-Extent-km^2")[["Unnamed: 0"] + month_list].head(-1).tail(-3).reset_index(drop=True).apply(pd.to_numeric)
    df_sie = df_sie.interpolate(method='linear')

    # Apply butterworth filter
    for month in month_list:
        df_sie[month] = filtfilt(B, A, df_sie[month])

    df_sie.rename({"Unnamed: 0": "Year"}, axis='columns', inplace=True)
    df_sie.insert(0, 'Sector', sector)

    df_sie["Year"] = pd.to_numeric(df_sie["Year"], downcast='integer')
    df_sie_list.append(df_sie)

df_sie = pd.concat(df_sie_list, ignore_index=True)

df_sie.to_pickle('pickles/sie.pkl')
# print(df_sie)