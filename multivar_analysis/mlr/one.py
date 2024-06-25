from scipy.stats import pearsonr
import scipy.signal as signal
import pandas as pd
from sklearn import linear_model

# Parameters

# Butterworth Filter
bw_order  = 1     # Filter order
bw_cfreq  = 0.4   # Cutoff frequency
B, A = signal.butter(bw_order, bw_cfreq, btype='low', analog=False)

sectors = {"Bell-Amundsen": None, "Indian": None, "Pacific": None, "Ross": None, "Weddell": None}
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

columns = ['Year'] + month_list

# Independent Variables (IVs)

# ENSO Data
dataset_path = rel_path + "darwin.anom_.txt"
df_soi = pd.read_csv(dataset_path, delim_whitespace=True, names=columns)
df_soi = df_soi[df_soi['Year']>=1979].head(-1).drop('Year', axis=1).reset_index(drop=True)

# PDO Data
dataset_path = rel_path + "ersst.v5.pdo.dat"
df_pdo = pd.read_csv(dataset_path, delim_whitespace=True, names=columns)
df_pdo = df_pdo[df_pdo['Year']>=1979].head(-1).drop('Year', axis=1).reset_index(drop=True)

print(df_soi)
print(df_pdo)

# Dependent Variable (DV)

# Sea Ice Index Data
dataset_path = rel_path + "S_Sea_Ice_Index_Regional_Monthly_Data_G02135_v3.0.xlsx"
for sector in list(sectors.keys()):
    sectors[sector] = pd.read_excel(dataset_path, sheet_name = sector + "-Extent-km^2")[month_list].head(-1).tail(-3).reset_index(drop=True).apply(pd.to_numeric)
    sectors[sector] = sectors[sector].interpolate(method='linear')

print(sectors)
exit()