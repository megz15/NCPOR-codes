from scipy.stats import pearsonr
import matplotlib.pyplot as plt
import scipy.signal as signal
import pandas as pd

def plot_graph(ax, extent_values, soi_values, month):
    ax.scatter(soi_values, extent_values, color='y', alpha=0.5)
    ax.set_title(month)

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

# ENSO Data
txt_path = rel_path + "darwin.anom_.txt"
columns = ['Year'] + month_list

df_soi = pd.read_csv(txt_path, delim_whitespace=True, names=columns)
df_soi = df_soi[df_soi['Year']>=1979].head(-1).reset_index()

# Sea Ice Index Data
excel_path = rel_path + "S_Sea_Ice_Index_Regional_Monthly_Data_G02135_v3.0.xlsx"
for sector in sectors:
    
    fig, axes = plt.subplots(3, 4, sharex=True, sharey=True)
    fig.suptitle(f"{sector} - Sea Ice Extent and ENSO Correlation (1979-2023)")

    print('\n'+sector)

    for i, month in enumerate(month_list):

        df_sea_ice = pd.read_excel(excel_path, sheet_name = sector + "-Extent-km^2").head(-1).tail(-3).reset_index()

        extent = pd.Series(df_sea_ice[month]).astype(float)
        extent = extent.interpolate(method='linear')

        # Butterworth Filter
        N  = 1    # Filter order
        Wn = 0.4  # Cutoff frequency
        B, A = signal.butter(N, Wn, output='ba')
        
        extent = pd.Series(signal.filtfilt(B,A, extent))
        df_soi[month] = pd.Series(signal.filtfilt(B,A, df_soi[month]))
        
        # Rank Transformation
        # extent = extent.transform("rank")
        # df_soi[month] = df_soi[month].transform("rank")

        a = pearsonr(df_soi[month], extent)
        if a[1] < 0.05: print("\033[0;32m", end='')
        print(f'{month}: {round(a[0], 3)} {round(a[1], 3)} \033[0m')

        row, col = divmod(i, 4)
        plot_graph(axes[row, col], extent, df_soi[month], month)
    
    handles, labels = plt.gca().get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper right')

    fig.supxlabel('SOI Index')
    fig.supylabel('Extent')

    plt.title(sector)
    plt.show()