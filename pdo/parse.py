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

rel_path = "../../data/"
columns = ['Year'] + month_list

# IOD Data
dataset_path = rel_path + "ersst.v5.pdo.dat"
df_pdo = pd.read_csv(dataset_path, delim_whitespace=True, names=columns)
df_pdo = df_pdo[df_pdo['Year']>=1979].head(-1).reset_index(drop=True)

# Apply butterworth filter
for month in month_list:
    df_pdo[month] = filtfilt(B, A, df_pdo[month])

df_pdo.to_pickle('pickles/pdo.pkl')

# print(df_pdo)