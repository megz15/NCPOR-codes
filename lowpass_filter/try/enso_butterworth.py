import scipy.signal as signal
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Load data

excel_path = "../../data/S_Sea_Ice_Index_Regional_Monthly_Data_G02135_v3.0.xlsx"

df_sea_ice = pd.read_excel(excel_path, "Ross-Extent-km^2").head(-1).tail(-3).reset_index()
year = pd.Series(df_sea_ice["Unnamed: 0"]).astype(int)
extent = pd.Series(df_sea_ice["January"]).astype(float)
extent = extent.interpolate(method='linear')

N  = 1    # Filter order
Wn = 0.4  # Cutoff frequency
B, A = signal.butter(N, Wn, output='ba')

extentf = signal.filtfilt(B,A, extent)

# Make plots
plt.figure(figsize=(13.66, 7.38), dpi=200)
fig = plt.figure(plt.figure(figsize=(13.66, 7.38), dpi=200))
ax1 = fig.add_subplot(211)
plt.plot(year, extent, 'b-')
plt.plot(year, extentf, 'r-',linewidth=2)
plt.legend(['Original','Filtered'])
plt.title("Sea Ice Extent for January over the Ross Sea region", fontsize=16, weight='bold', pad=20)
ax1.axes.get_xaxis().set_visible(False)

ax1 = fig.add_subplot(212)
plt.plot(year,extent-extentf, 'b-')
plt.legend(['Residuals'])

plt.xticks(fontsize=12, weight='bold')

fig.supxlabel("Year", fontsize=15, weight='bold')
fig.supylabel("Extent (km^2)", fontsize=15, weight='bold')

# plt.show()

plt.tight_layout()
plt.savefig('results/filter/ch4/ross_jan_sie.png')
plt.close()