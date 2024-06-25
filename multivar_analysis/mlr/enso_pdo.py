from scipy.stats import pearsonr
import matplotlib.pyplot as plt
import scipy.signal as signal
import pandas as pd

def plot_graph(ax, x_values, y_values, month):
    ax.scatter(x_values, y_values, color='y', alpha=0.5)
    ax.set_title(month)

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

# Butterworth Filter Params
N  = 1    # Filter order
Wn = 0.4  # Cutoff frequency
B, A = signal.butter(N, Wn, output='ba')

# ENSO Data
txt_path = rel_path + "darwin.anom_.txt"
columns = ['Year'] + month_list

df_soi = pd.read_csv(txt_path, delim_whitespace=True, names=columns)
df_soi = df_soi[df_soi['Year']>=1979].head(-1).reset_index()

# PDO Data
txt_path = rel_path + "ersst.v5.pdo.dat"
columns = ['Year'] + month_list

df_pdo = pd.read_csv(txt_path, delim_whitespace=True, names=columns)
df_pdo = df_pdo[df_pdo['Year']>=1979].head(-1).reset_index()

fig, axes = plt.subplots(3, 4, sharex=True, sharey=True)
fig.suptitle("ENSO and PDO Correlation (1979-2023)")

for i, month in enumerate(month_list):
    
    # df_soi[month] = pd.Series(signal.filtfilt(B,A, df_soi[month]))
    
    # Rank Transformation
    # extent = extent.transform("rank")
    # df_soi[month] = df_soi[month].transform("rank")

    a = pearsonr(df_soi[month], df_pdo[month])
    if a[1] < 0.05: print("\033[0;32m", end='')
    print(f'{month}: {round(a[0], 3)} {round(a[1], 3)} \033[0m')

    row, col = divmod(i, 4)
    plot_graph(axes[row, col], df_soi[month], df_pdo[month], month)

handles, labels = plt.gca().get_legend_handles_labels()
fig.legend(handles, labels, loc='upper right')

fig.supxlabel('ENSO')
fig.supylabel('PDO')
plt.show()