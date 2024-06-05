pearson_threshold = 0.4
banner_width = 54

print("="*banner_width)
print("Pearson Correlation Coefficient Values".center(banner_width))
print("between Sea Ice Extent & POD Indices".center(banner_width))
print("from 1979 to 2023".center(banner_width))
print("="*banner_width)

import matplotlib.pyplot as plt
import scipy.signal as signal
import pandas as pd
import numpy as np

def Average(lst): return round(sum(lst)/len(lst), 3)

def plot_graph(ax, year, extent, bfl_values, month):
    ax.plot(year, extent, label='Data')
    ax.plot(year, bfl_values, color='red', label='Best Fit Line')
    ax.set_xlabel('Year')
    ax.set_ylabel('Extent')
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

corr_values, minima_corr_values, minima_below_bfl_corr_values, maxima_corr_values, maxima_above_bfl_corr_values = [], [], [], [], []

max_template = {
    "value": 0,
    "month": '',
    "sector": '',
}

max_corr_dict = {
    "max_corr": max_template.copy(),
    "max_minima_corr": max_template.copy(),
    "max_minima_below_bfl_corr": max_template.copy(),
    "max_maxima_corr": max_template.copy(),
    "max_maxima_above_bfl_corr": max_template.copy(),
}

# PDO Data
txt_path = rel_path + "ersst.v5.pdo.dat"
columns = ['Year'] + month_list

df_pdo = pd.read_csv(txt_path, delim_whitespace=True, names=columns)
df_pdo = df_pdo[df_pdo['Year']>=1979].head(-1).reset_index()

# Sea Ice Index Data
excel_path = rel_path + "S_Sea_Ice_Index_Regional_Monthly_Data_G02135_v3.0.xlsx"
for sector in sectors:
    
    # fig, axes = plt.subplots(3, 4, sharex=True, sharey=True)
    # fig.suptitle(f"{sector} - Sea Ice Extent and PDO Correlation (1979-2023)")

    for i, month in enumerate(month_list):

        df_sea_ice = pd.read_excel(excel_path, sheet_name = sector + "-Extent-km^2").head(-1).tail(-3).reset_index()

        year = pd.Series(df_sea_ice["Unnamed: 0"]).astype(int)
        extent = pd.Series(df_sea_ice[month]).astype(float)

        extent = extent.interpolate(method='linear')
        
        # Rank Transformation
        extent = extent.transform("rank")

        # # Butterworth Filter
        # N  = 2    # Filter order
        # Wn = 0.6  # Cutoff frequency
        # B, A = signal.butter(N, Wn, output='ba')
        # extent = pd.Series(signal.filtfilt(B,A, extent)) - extent
        # # residual = extent-extentf

        extent_diff = np.diff(extent, 1)

        local_minima_indices = np.where((extent_diff[:-1] < 0) & (extent_diff[1:] > 0))[0] + 1
        local_minima_values = extent[local_minima_indices]

        local_maxima_indices = np.where((extent_diff[:-1] > 0) & (extent_diff[1:] < 0))[0] + 1
        local_maxima_values = extent[local_maxima_indices]

        m, b = np.polyfit(year, extent, 1)
        bfl_values = m*year + b

        minima_below_bfl_indices = [i for i in local_minima_indices if extent[i] < bfl_values[i]]
        minima_below_bfl_values = extent[minima_below_bfl_indices]
        
        maxima_above_bfl_indices = [i for i in local_maxima_indices if extent[i] > bfl_values[i]]
        maxima_above_bfl_values = extent[maxima_above_bfl_indices]

        curr_corr = round(extent.corr(df_pdo[month], method='pearson'), 3)
        if abs(curr_corr) > abs(max_corr_dict["max_corr"]['value']):
            max_corr_dict["max_corr"]['value'] = curr_corr
            max_corr_dict["max_corr"]['month'] = month
            max_corr_dict["max_corr"]['sector'] = sector
        corr_values.append(curr_corr)

        curr_minima_corr = round(local_minima_values.corr(df_pdo[month][local_minima_indices], method='pearson'), 3)
        if abs(curr_minima_corr) > abs(max_corr_dict["max_minima_corr"]['value']):
            max_corr_dict["max_minima_corr"]['value'] = curr_minima_corr
            max_corr_dict["max_minima_corr"]['month'] = month
            max_corr_dict["max_minima_corr"]['sector'] = sector
        minima_corr_values.append(curr_minima_corr)

        curr_minima_below_bfl_corr = round(minima_below_bfl_values.corr(df_pdo[month][minima_below_bfl_indices], method='pearson'), 3)
        if abs(curr_minima_below_bfl_corr) > abs(max_corr_dict["max_minima_below_bfl_corr"]['value']):
            max_corr_dict["max_minima_below_bfl_corr"]['value'] = curr_minima_below_bfl_corr
            max_corr_dict["max_minima_below_bfl_corr"]['month'] = month
            max_corr_dict["max_minima_below_bfl_corr"]['sector'] = sector
        minima_below_bfl_corr_values.append(curr_minima_below_bfl_corr)

        curr_maxima_corr = round(local_maxima_values.corr(df_pdo[month][local_maxima_indices], method='pearson'), 3)
        if abs(curr_maxima_corr) > abs(max_corr_dict["max_maxima_corr"]['value']):
            max_corr_dict["max_maxima_corr"]['value'] = curr_maxima_corr
            max_corr_dict["max_maxima_corr"]['month'] = month
            max_corr_dict["max_maxima_corr"]['sector'] = sector
        maxima_corr_values.append(curr_maxima_corr)

        curr_maxima_above_bfl_corr = round(maxima_above_bfl_values.corr(df_pdo[month][maxima_above_bfl_indices], method='pearson'), 3)
        if abs(curr_maxima_above_bfl_corr) > abs(max_corr_dict["max_maxima_above_bfl_corr"]['value']):
            max_corr_dict["max_maxima_above_bfl_corr"]['value'] = curr_maxima_above_bfl_corr
            max_corr_dict["max_maxima_above_bfl_corr"]['month'] = month
            max_corr_dict["max_maxima_above_bfl_corr"]['sector'] = sector
        maxima_above_bfl_corr_values.append(curr_maxima_above_bfl_corr)

        # row, col = divmod(i, 4)
        # plot_graph(axes[row, col], year, extent, bfl_values, month)

    print(f"\n\033[0;31m{sector.ljust(10)}\t\033[0;33mCorr\tMin\tMinBB\tMax\tMaxAB\033[0m")
    for i in range(len(month_list)):
        
        print(month_list[i].ljust(10), end='\t')
        print(("\033[0;32m" if abs(corr_values[i]) > pearson_threshold else "") + str(corr_values[i]) + "\033[0m", end='\t')
        
        print(("\033[0;32m" if abs(minima_corr_values[i]) > pearson_threshold else "") + str(minima_corr_values[i]) + "\033[0m", end='\t')
        print(("\033[0;32m" if abs(minima_below_bfl_corr_values[i]) > pearson_threshold else "") + str(minima_below_bfl_corr_values[i]) + "\033[0m", end='\t')
        
        print(("\033[0;32m" if abs(maxima_corr_values[i]) > pearson_threshold else "") + str(maxima_corr_values[i]) + "\033[0m", end='\t')
        print(("\033[0;32m" if abs(maxima_above_bfl_corr_values[i]) > pearson_threshold else "") + str(maxima_above_bfl_corr_values[i]) + "\033[0m", end='\n')
    
    print(f"\033[0;33mAverage\t\t{Average(corr_values)}\t{Average(minima_corr_values)}\t{Average(minima_below_bfl_corr_values)}\t{Average(maxima_corr_values)}\t{Average(maxima_above_bfl_corr_values)}\033[0m")

    corr_values.clear()
    minima_corr_values.clear()
    minima_below_bfl_corr_values.clear()
    maxima_corr_values.clear()
    maxima_above_bfl_corr_values.clear()

    # plt.show()

for name, val in max_corr_dict.items():
    print()
    for i in ('value', 'month', 'sector'):
        print(f"{name} {i} : {val[i]}")