pearson_threshold = 0.4
banner_width = 54

print("="*banner_width)
print("Pearson Correlation Coefficient Values".center(banner_width))
print("between Sea Ice Extent & ENSO Indices".center(banner_width))
print("from 1979 to 2023".center(banner_width))
print("="*banner_width)

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def Average(lst): return round(sum(lst)/len(lst), 3)

def plot_graph(sector, year, extent, bfl_values):
    plt.plot(year, extent, label='Data')
    plt.plot(year, bfl_values, color='red', label='Best Fit Line')
    plt.xlabel('Year')
    plt.ylabel('Extent')
    plt.title(sector)
    plt.legend()
    plt.show()

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

corr_values = []

# Sea Ice Index Data
excel_path = "./S_Sea_Ice_Index_Regional_Monthly_Data_G02135_v3.0.xlsx"

df_sea_ice = pd.read_excel(excel_path, None)
for sheet in [x for x in df_sea_ice.keys() if "Extent" in x]:

    sector = sheet[:-12]

    for month in month_list:

        df_sea_ice = pd.read_excel(excel_path, sheet_name=sheet).head(-1).tail(-3).reset_index()

        year = pd.Series(df_sea_ice["Unnamed: 0"]).astype(int)
        extent = pd.Series(df_sea_ice[month]).astype(float)

        extent = extent.interpolate(method='linear')

        extent_diff = np.diff(extent, 1)

        m, b = np.polyfit(year, extent, 1)
        bfl_values = m*year + b

        # ENSO Data

        txt_path = "./darwin.anom_.txt"
        columns = ['Year'] + month_list

        df_soi = pd.read_csv(txt_path, delim_whitespace=True, names=columns)
        df_soi = df_soi[df_soi['Year']>=1979].reset_index()

        curr_corr = round(extent.corr(df_soi[month], method='pearson'), 3)
        corr_values.append(curr_corr)

    print(f"\n\033[0;31m{sector.ljust(10)}\t\033[0;33mCorr\033[0m")
    for i in range(len(month_list)):
        
        print(month_list[i].ljust(10), end='\t')
        print(("\033[0;32m" if abs(corr_values[i]) > pearson_threshold else "") + str(corr_values[i]) + "\033[0m", end='\n')

    corr_values.clear()

    # plot_graph(sector, year, extent, bfl_values)