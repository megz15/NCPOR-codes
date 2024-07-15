import pandas as pd
from scipy.signal import butter, filtfilt

# Butterworth Filter
bw_order  = 1     # Filter order
bw_cfreq  = 0.4   # Cut-off freq
B,A = butter(bw_order, bw_cfreq, btype="high")

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

rel_path = "../../data/"
columns = ['Year'] + month_list

# IOD Data
dataset_path = rel_path + "darwin.anom_.txt"
df_soi = pd.read_csv(dataset_path, delim_whitespace=True, names=columns)
df_soi = df_soi[df_soi['Year']>=1979].head(-1).reset_index(drop=True)

# Apply butterworth filter
for month in month_list:
    df_soi[month] = filtfilt(B, A, df_soi[month])

df_soi.to_pickle('pickles/high_soi.pkl')

# print(df_soi)