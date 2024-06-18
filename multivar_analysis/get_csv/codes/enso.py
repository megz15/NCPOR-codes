import matplotlib.pyplot as plt
import scipy.signal as signal
import pandas as pd
import numpy as np
from scipy.stats import pearsonr

def Average(lst): return round(sum(lst)/len(lst), 3)

def plot_graph(ax, year, extent_values, bfl_seaice, soi_values, bfl_soi, month):
    ax.plot(year, extent_values, color='b', label='Extent')
    ax.plot(year, bfl_seaice, color='g', label='Extent Best Fit')
    ax.plot(year, soi_values, color='r', label='ENSO')
    ax.plot(year, bfl_soi, color='y', label='ENSO Best Fit')
    ax.legend()
    ax.set_title(month)

sectors = ["Bell-Amundsen", "Indian", "Pacific", "Ross", "Weddell"]
rel_path = "../../data/"
pearson_threshold = 0.5

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

json_export = {sector: {month: 0 for month in month_list} for sector in sectors}

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

    for i, month in enumerate(month_list):

        df_sea_ice = pd.read_excel(excel_path, sheet_name = sector + "-Extent-km^2").head(-1).tail(-3).reset_index()

        year = pd.Series(df_sea_ice["Unnamed: 0"]).astype(int)
        extent = pd.Series(df_sea_ice[month]).astype(float)

        extent = extent.interpolate(method='linear')

        # Butterworth Filter
        N  = 1    # Filter order
        Wn = 0.4  # Cutoff frequency
        B, A = signal.butter(N, Wn, output='ba')
        
        extent = pd.Series(signal.filtfilt(B,A, extent))
        df_soi[month] = pd.Series(signal.filtfilt(B,A, df_soi[month]))
        

        # Rank Transformation
        extent = extent.transform("rank")
        df_soi[month] = df_soi[month].transform("rank")

        extent_diff = np.diff(extent, 1)

        local_minima_indices = np.where((extent_diff[:-1] < 0) & (extent_diff[1:] > 0))[0] + 1
        local_minima_values = extent[local_minima_indices]

        local_maxima_indices = np.where((extent_diff[:-1] > 0) & (extent_diff[1:] < 0))[0] + 1
        local_maxima_values = extent[local_maxima_indices]

        # 5th-degree polynomial fit for sea ice extent
        coefficients_seaice = np.polyfit(year, extent, 5)
        bfl_values_seaice = np.polyval(coefficients_seaice, year)

        # 5th-degree polynomial fit for ENSO
        coefficients_soi = np.polyfit(year, df_soi[month], 5)
        bfl_values_soi = np.polyval(coefficients_soi, year)

        minima_below_bfl_indices = [i for i in local_minima_indices if extent[i] < bfl_values_seaice[i]]
        minima_below_bfl_values = extent[minima_below_bfl_indices]
        
        maxima_above_bfl_indices = [i for i in local_maxima_indices if extent[i] > bfl_values_seaice[i]]
        maxima_above_bfl_values = extent[maxima_above_bfl_indices]

        # curr_corr = round(extent.corr(df_soi[month], method='pearson'), 3)
        curr_corr, p_val_curr = pearsonr(extent, df_soi[month])
        curr_corr = round(curr_corr, 3)
        p_val_curr = round(p_val_curr, 3)

        json_export[sector][month] = (curr_corr, p_val_curr)

        if abs(curr_corr) > abs(max_corr_dict["max_corr"]['value']):
            max_corr_dict["max_corr"]['value'] = curr_corr
            max_corr_dict["max_corr"]['month'] = month
            max_corr_dict["max_corr"]['sector'] = sector
        corr_values.append(curr_corr)

        curr_minima_corr = round(local_minima_values.corr(df_soi[month][local_minima_indices], method='pearson'), 3)
        if abs(curr_minima_corr) > abs(max_corr_dict["max_minima_corr"]['value']):
            max_corr_dict["max_minima_corr"]['value'] = curr_minima_corr
            max_corr_dict["max_minima_corr"]['month'] = month
            max_corr_dict["max_minima_corr"]['sector'] = sector
        minima_corr_values.append(curr_minima_corr)

        curr_minima_below_bfl_corr = round(minima_below_bfl_values.corr(df_soi[month][minima_below_bfl_indices], method='pearson'), 3)
        if abs(curr_minima_below_bfl_corr) > abs(max_corr_dict["max_minima_below_bfl_corr"]['value']):
            max_corr_dict["max_minima_below_bfl_corr"]['value'] = curr_minima_below_bfl_corr
            max_corr_dict["max_minima_below_bfl_corr"]['month'] = month
            max_corr_dict["max_minima_below_bfl_corr"]['sector'] = sector
        minima_below_bfl_corr_values.append(curr_minima_below_bfl_corr)

        curr_maxima_corr = round(local_maxima_values.corr(df_soi[month][local_maxima_indices], method='pearson'), 3)
        if abs(curr_maxima_corr) > abs(max_corr_dict["max_maxima_corr"]['value']):
            max_corr_dict["max_maxima_corr"]['value'] = curr_maxima_corr
            max_corr_dict["max_maxima_corr"]['month'] = month
            max_corr_dict["max_maxima_corr"]['sector'] = sector
        maxima_corr_values.append(curr_maxima_corr)

        curr_maxima_above_bfl_corr = round(maxima_above_bfl_values.corr(df_soi[month][maxima_above_bfl_indices], method='pearson'), 3)
        if abs(curr_maxima_above_bfl_corr) > abs(max_corr_dict["max_maxima_above_bfl_corr"]['value']):
            max_corr_dict["max_maxima_above_bfl_corr"]['value'] = curr_maxima_above_bfl_corr
            max_corr_dict["max_maxima_above_bfl_corr"]['month'] = month
            max_corr_dict["max_maxima_above_bfl_corr"]['sector'] = sector
        maxima_above_bfl_corr_values.append(curr_maxima_above_bfl_corr)

        row, col = divmod(i, 4)
        plot_graph(axes[row, col], year, extent, bfl_values_seaice, df_soi[month], bfl_values_soi, month)

    corr_values.clear()
    minima_corr_values.clear()
    minima_below_bfl_corr_values.clear()
    maxima_corr_values.clear()
    maxima_above_bfl_corr_values.clear()

    plt.show()

# import json
# with open("multivar_analysis/get_csv/data/enso.json", 'w') as f:
#     json.dump(json_export, f)