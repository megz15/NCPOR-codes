import pandas as pd
from scipy.stats import pearsonr

df_iod = pd.read_pickle('iod/iod.pkl')
df_sie = pd.read_pickle('sie/sie.pkl')

sectors = ["Bell-Amundsen", "Indian", "Pacific", "Ross", "Weddell"]

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

for sector in sectors:
    df_sie_sector = df_sie[df_sie['Sector'] == sector]

    print(f"\n\033[0;31m{sector.ljust(10)}\t\033[0;33mCorr\tp-Value\033[0m")
    for month in month_list:
        corr, pval = [round(x,3) for x in pearsonr(df_sie_sector[month], df_iod[month])]

        print(month.ljust(10), end='\t')
        print(("\033[0;32m" if pval < 0.05 else "") + str(corr) + "\033[0m", end='\t')
        print(pval)