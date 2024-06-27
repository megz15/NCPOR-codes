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

sns.heatmap(corr_df, annot=False, cmap='coolwarm', center=0, cbar_kws={'label': 'Correlation Coefficient', "shrink": 0.5}, square=True)

for i in range(corr_df.shape[0]):
    for j in range(corr_df.shape[1]):
        corr_value = corr_df.iloc[i, j]
        pval_value = pval_df.iloc[i, j]
        text = f'{corr_value}\n({pval_value})'
        
        if pval_value < 0.05:
            bbox_props = dict(boxstyle="round,pad=0.2", facecolor="lime", edgecolor="none")
        else:
            bbox_props = dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="none")
        
        plt.text(j + 0.5, i + 0.5, text, ha='center', va='center', color='black', bbox=bbox_props, fontsize=12)

plt.title(f'Correlation Coefficients and p-values between Antarctic Sea Ice Extent and {dataset.upper()}', fontsize=14)
plt.xlabel('Month', fontsize=14)
plt.ylabel('Region', fontsize=14)

plt.tight_layout()
plt.show()