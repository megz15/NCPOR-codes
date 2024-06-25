from scipy.stats import pearsonr
import matplotlib.pyplot as plt
import scipy.signal as signal
import pandas as pd

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

# Butterworth Filter params
bw_order  = 1     # Filter order
bw_cfreq  = 0.4   # Cutoff frequency
B, A = signal.butter(bw_order, bw_cfreq, btype='low', analog=False)

columns = ['Year'] + month_list

# ENSO Data
txt_path = rel_path + "darwin.anom_.txt"

df_soi = pd.read_csv(txt_path, delim_whitespace=True, names=columns)
df_soi = df_soi[df_soi['Year']>=1979].head(-1).reset_index()

# PDO Data
txt_path = rel_path + "ersst.v5.pdo.dat"

df_pdo = pd.read_csv(txt_path, delim_whitespace=True, names=columns)
df_pdo = df_pdo[df_pdo['Year']>=1979].head(-1).reset_index()

# Combine
enso_values = df_soi[month_list].values.flatten()
pdo_values = df_pdo[month_list].values.flatten()

# Applying Butterworth Filter
enso_values = pd.Series(signal.filtfilt(B,A, enso_values))
pdo_values = pd.Series(signal.filtfilt(B,A, pdo_values))

corr, p_value = pearsonr(enso_values, pdo_values)
print(f'Overall Pearson Correlation: {round(corr, 3)}, p-value: {round(p_value, 3)}')

fig, ax = plt.subplots()
ax.scatter(enso_values, pdo_values, color='y', alpha=0.5)
ax.set_title("ENSO vs PDO (1979-2023)")

fig.supxlabel('ENSO')
fig.supylabel('PDO')
plt.show()

# fig, axes = plt.subplots(3, 4, sharex=True, sharey=True)
# fig.suptitle("ENSO and PDO Correlation (1979-2023)")

# for i, month in enumerate(month_list):
    
#     # Applying Butterworth Filter
#     df_soi[month] = pd.Series(signal.filtfilt(B,A, df_soi[month]))
#     df_pdo[month] = pd.Series(signal.filtfilt(B,A, df_pdo[month]))
    
#     # Applying Rank Transformation
#     # df_soi[month] = df_soi[month].transform("rank")
#     # df_pdo[month] = df_pdo[month].transform("rank")

#     a = pearsonr(df_soi[month], df_pdo[month])
#     if a[1] < 0.05: print("\033[0;32m", end='')
#     print(f'{month}: {round(a[0], 3)} {round(a[1], 3)} \033[0m')

#     row, col = divmod(i, 4)
#     plot_graph(axes[row, col], df_soi[month], df_pdo[month], month)

# handles, labels = plt.gca().get_legend_handles_labels()
# fig.legend(handles, labels, loc='upper right')

# fig.supxlabel('ENSO')
# fig.supylabel('PDO')
# plt.show()