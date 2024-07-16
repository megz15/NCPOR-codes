import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

btypes = ["low", "high"]
datasets = ["enso", "pdo", "ssr", "str", "iod"]

for btype in btypes:
    for dataset in datasets:

        with open(f'multivar_analysis/get_corr_json/data/{btype}/{btype}_{dataset}.json') as f:
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

        corr_df.rename(index={'Bell-Amundsen': 'Bell-Am'}, inplace=True)
        pval_df.rename(index={'Bell-Amundsen': 'Bell-Am'}, inplace=True)

        corr_df = corr_df.loc[["Weddell", "Indian", "Pacific", "Ross", "Bell-Am"]]
        pval_df = pval_df.loc[["Weddell", "Indian", "Pacific", "Ross", "Bell-Am"]]

        corr_df.columns = corr_df.columns.map(lambda x: x[:3])
        pval_df.columns = pval_df.columns.map(lambda x: x[:3])

        plt.figure(figsize=(13.66, 7.38), dpi=200)

        ax = sns.heatmap(corr_df, annot=False, cmap='coolwarm', center=0, cbar_kws={'location': 'bottom', 'aspect': 40})

        for i in range(corr_df.shape[0]):
            for j in range(corr_df.shape[1]):
                corr_value = corr_df.iloc[i, j]
                pval_value = pval_df.iloc[i, j]
                text = f'{corr_value}\n({pval_value})'
                
                if pval_value < 0.05:
                    bbox_props = dict(boxstyle="round,pad=0.2", facecolor="lime", edgecolor="none")
                else:
                    bbox_props = dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="none")
                
                plt.text(j + 0.5, i + 0.5, text, ha='center', va='center', color='black', bbox=bbox_props, fontsize=12, weight="bold")

        plt.title(f'Correlation Coefficients and p-values between {btype}-pass Antarctic Sea Ice Extent and {dataset.upper()}', fontsize=16, weight='bold', pad=20)
        plt.xlabel('Month', fontsize=15, labelpad=10, weight='bold')
        plt.ylabel('Region', fontsize=15, labelpad=10, weight='bold')

        ax.set_xticklabels(ax.get_xticklabels(), fontsize=14, weight='bold')
        ax.set_yticklabels(ax.get_yticklabels(), fontsize=14, weight='bold')

        colorbar = ax.collections[0].colorbar
        colorbar.ax.tick_params(labelsize=15, width=2)

        output_dir = f"results/heatmap/{btype}"

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        plt.savefig(os.path.join(output_dir, f'{dataset}_{btype}.png'))
        plt.close()

        plt.tight_layout()
        # plt.show()