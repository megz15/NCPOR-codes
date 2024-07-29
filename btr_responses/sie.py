import pandas as pd
import os
from scipy.signal import butter, filtfilt
import matplotlib.pyplot as plt

# Butterworth Filter parameters
bw_order = 1  # Filter order
bw_cfreq = 0.4  # Cut-off frequency

B_low, A_low = butter(bw_order, bw_cfreq, btype="low")
B_high, A_high = butter(bw_order, bw_cfreq, btype="high")

sectors = ["Bell-Amundsen", "Indian", "Pacific", "Ross", "Weddell"]
rel_path = "../../data/"

month_list = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
]

for sector in sectors:
    dataset_path = rel_path + "S_Sea_Ice_Index_Regional_Monthly_Data_G02135_v3.0.xlsx"

    df_sie = pd.read_excel(dataset_path, sheet_name=sector + "-Extent-km^2")[["Unnamed: 0"] + month_list].head(-1).tail(-3).reset_index(drop=True).apply(pd.to_numeric)
    df_sie = df_sie.interpolate(method='linear')
    df_sie.rename({"Unnamed: 0": "Year"}, axis='columns', inplace=True)
    df_sie["Year"] = pd.to_numeric(df_sie["Year"], downcast='integer')

    plt.figure(figsize=(13.66, 7.38), dpi=200)
    fig, axes = plt.subplots(nrows=3, ncols=4, figsize=(13.66, 7.38), dpi=200)
    fig.suptitle(f'Sea Ice Extent for {sector if sector!="Bell-Amundsen" else "Bellingshausen-Amundsen"} {"Ocean" if sector in ["Indian", "Pacific"] else "Sea"} Sector', fontsize=18, weight='bold')

    for i, month in enumerate(month_list):
        ax = axes[i//4, i%4]
        time_series = df_sie[month].values
        
        low_passed = filtfilt(B_low, A_low, time_series)
        high_passed = filtfilt(B_high, A_high, time_series)
        
        ax.plot(df_sie["Year"], time_series, label="Original", color='blue')
        ax.plot(df_sie["Year"], low_passed, label="Low-pass Filtered", color='red')
        ax.plot(df_sie["Year"], high_passed, label="High-pass Filtered", color='green')
        ax.set_title(month[:3], fontsize=12, weight='bold')
        ax.grid(True)

    fig.supxlabel('Year', fontsize=15, weight='bold')
    fig.supylabel('Extent (km^2)', fontsize=15, weight='bold')

    plt.tight_layout()

    output_dir = f"results/filter/SIE/"

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    plt.savefig(os.path.join(output_dir, f'{sector}.png'))
    plt.close()

    # plt.show()