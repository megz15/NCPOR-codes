import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def lanc(numwt, haf):
    summ = 0
    numwt += 1
    wt = np.zeros(numwt)

    # Filter weights.
    ii = np.arange(numwt)
    wt = 0.5 * (1.0 + np.cos(np.pi * ii * 1.0 / numwt))
    ii = np.arange(1, numwt)
    xx = np.pi * 2 * haf * ii
    wt[1 : numwt + 1] = wt[1 : numwt + 1] * np.sin(xx) / xx
    summ = wt[1 : numwt + 1].sum()
    xx = wt.sum() + summ
    wt /= xx
    return np.r_[wt[::-1], wt[1 : numwt + 1]]

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
month = "January"

txt_path = "../../data/darwin.anom_.txt"
excel_path = "../../data/S_Sea_Ice_Index_Regional_Monthly_Data_G02135_v3.0.xlsx"

df_soi = pd.read_csv(txt_path, delim_whitespace=True, names=(['Year'] + month_list))
df_soi = df_soi[df_soi['Year']>=1979].head(-1).reset_index()

df_sea_ice = pd.read_excel(excel_path, "Ross-Extent-km^2").head(-1).tail(-3).reset_index()
year = pd.Series(df_sea_ice["Unnamed: 0"]).astype(int)
extent = pd.Series(df_sea_ice[month]).astype(float)
extent = extent.interpolate(method='linear')

wt = lanc(5 + 1 + 5, 1/40)
low = np.convolve(wt, extent, mode="same")
high = extent - low

fig, (ax0, ax1, axo) = plt.subplots(nrows=3)

ax0.plot(high, label="high")
ax1.plot(low, label="low")
axo.plot(extent, label="orig")

ax0.legend(numpoints=1)
ax1.legend(numpoints=1)
axo.legend(numpoints=1)

plt.show()