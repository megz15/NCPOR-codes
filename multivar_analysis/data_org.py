import pandas as pd

regions = ["Bell-Amundsen", "Indian", "Pacific", "Ross", "Weddell"]
datasets = ["enso", "pdo", "ssr", "str"]

rel_path = "multivar_analysis/"

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

region_dfs = {region: pd.DataFrame({'Month': month_list}) for region in regions}

for region in regions:
    for dataset in datasets:
        df = pd.read_json(rel_path + "get_csv/data/" + dataset + ".json")
        region_dfs[region][dataset] = [x[0] for x in df[region].values]

print(region_dfs)