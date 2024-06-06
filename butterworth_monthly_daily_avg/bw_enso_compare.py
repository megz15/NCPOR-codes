import pandas as pd
import numpy as np
import scipy.signal as signal
import matplotlib.pyplot as plt

bw_order = 3
bw_cfreq = 0.5
b, a = signal.butter(bw_order, bw_cfreq, btype='low', analog=False)

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

df_original = df_soi.copy()

for month in month_days.keys():
    df_soi[month] = signal.filtfilt(b, a, df_soi[month])

comparison_df = pd.DataFrame()
comparison_df['Year'] = df_soi['Year']

for month in month_days.keys():
    comparison_df[f'Original_{month}'] = df_original[month]
    comparison_df[f'Filtered_{month}'] = df_soi[month]
    comparison_df[f'Difference_{month}'] = df_soi[month] - df_original[month]

# Plotting the data
fig, axes = plt.subplots(4, 3, figsize=(15, 10), sharex=True)
axes = axes.flatten()

for i, month in enumerate(month_days.keys()):
    ax = axes[i]
    ax.plot(comparison_df['Year'], comparison_df[f'Original_{month}'], label='Original', color='blue')
    ax.plot(comparison_df['Year'], comparison_df[f'Filtered_{month}'], label='Filtered', color='red')
    ax.set_title(month)
    ax.legend()

fig.tight_layout()
plt.show()