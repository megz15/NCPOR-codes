import matplotlib.pyplot as plt
import pandas as pd
import scipy.signal as signal

year_list = list(range(1979, 2024))

# Sea Ice Index Data
excel_path = "../../data/S_Sea_Ice_Index_Regional_Daily_Data_G02135_v3.0.xlsx"
df_sea_ice = pd.read_excel(excel_path, sheet_name="Bell-Amundsen-Extent-km^2")
df_sea_ice.drop(df_sea_ice.columns[[-1, 0, 1, 2]],axis=1,inplace=True)

extent = pd.Series(df_sea_ice[[year for year in year_list]].values.ravel()).astype(float).interpolate(method='linear')

# Butterworth Filter
N  = 2    # Filter order
Wn = 0.6  # Cutoff frequency
B, A = signal.butter(N, Wn, output='ba')
extentf = pd.Series(signal.filtfilt(B,A, extent))
residual = extent-extentf

fig, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=True)
fig.suptitle("Sea Ice Extent")
fig.supylabel('Extent (km^2)')
fig.supxlabel('Days since Jan 1 1979')

extent.plot(color='blue', ax=ax1)
ax1.legend(['Original'])

extentf.plot(color='orange', ax=ax2)
ax2.legend(['Low Pass'])

residual.plot(color='green', ax=ax3)
ax3.legend(['High Pass'])

plt.show()