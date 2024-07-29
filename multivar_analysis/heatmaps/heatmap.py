import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

dataset = ["enso", "pdo", "ssr", "str", "iod"][-1]

with open(f'multivar_analysis/get_corr_json/data/{dataset}.json') as f:
    data = json.load(f)

regions = list(data.keys())
months = list(data[regions[0]].keys())

corr_data = []
pval_data = []
for region in regions:
    corr_row = []
    pval_row = []
    for month in months:
        corr_row.append(data[region][month][0])
        pval_row.append(data[region][month][1])
    corr_data.append(corr_row)
    pval_data.append(pval_row)

corr_df = pd.DataFrame(corr_data, index=regions, columns=months)
pval_df = pd.DataFrame(pval_data, index=regions, columns=months)

plt.figure(figsize=(15, 10))

plt.subplot(2, 1, 1)
sns.heatmap(corr_df, annot=True, cmap='coolwarm', center=0, cbar_kws={'label': 'Correlation Coefficient'})
plt.title(f'Correlation Coefficients between Antarctic Sea Ice Extent and {dataset.upper()}')
plt.xlabel('Month')
plt.ylabel('Region')

plt.subplot(2, 1, 2)
sns.heatmap(pval_df, annot=True, cmap='viridis_r', cbar_kws={'label': 'p-value'})
plt.title('p-values for Correlations')
plt.xlabel('Month')
plt.ylabel('Region')

plt.tight_layout()
plt.show()