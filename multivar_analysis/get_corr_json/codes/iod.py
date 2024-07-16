import json
import pandas as pd
from scipy.stats import pearsonr

btype = "low"

df_iod = pd.read_pickle(f'pickles/{btype}_iod.pkl')
df_sie = pd.read_pickle(f'pickles/{btype}_sie.pkl')

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

json_export = {sector: {month: 0 for month in month_list} for sector in sectors}

for sector in sectors:
    df_sie_sector = df_sie[df_sie['Sector'] == sector]

    for month in month_list:
        json_export[sector][month] = [round(x,3) for x in pearsonr(df_sie_sector[month], df_iod[month])]
        
with open(f"multivar_analysis/get_corr_json/data/{btype}/{btype}_iod.json", 'w') as f:
    json.dump(json_export, f)