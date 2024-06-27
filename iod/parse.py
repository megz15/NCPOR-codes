import pandas as pd
from scipy.signal import butter, filtfilt

# Butterworth Filter
bw_order  = 1     # Filter order
bw_cfreq  = 0.4   # Cut-off freq
B,A = butter(bw_order, bw_cfreq)

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

rel_path = "../../data/iod/"
columns = ['Year'] + month_list

# IOD Data
dataset_path = rel_path + "dmi.had.long.data"
df_iod = pd.read_csv(dataset_path, delim_whitespace=True, names=columns, skiprows=1, skipfooter=8, engine='python')
df_iod = df_iod[df_iod['Year']>=1979].drop('Year', axis=1).reset_index(drop=True)

# Apply butterworth filter
for month in month_list:
    df_iod[month] = filtfilt(B, A, df_iod[month])

print(df_iod)