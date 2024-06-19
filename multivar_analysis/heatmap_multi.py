import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def load_json(fp):
    with open(fp, 'r') as file:
        return json.load(file)
    
file_paths = {}

datasets = ["enso", "pdo", "ssr", "str"]

for dataset in datasets:
    file_paths[dataset] = f'multivar_analysis/get_csv/data/{dataset}.json'

# Load all data
data = {index: load_json(file_path) for index, file_path in file_paths.items()}

# Function to create DataFrames for correlation coefficients and p-values
def create_dataframes(data):
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
    return corr_df, pval_df

# Create DataFrames for each index
dataframes = {index: create_dataframes(data[index]) for index in data.keys()}

# Combine all correlation coefficients into one DataFrame
combined_corr_df = pd.concat(
    [df[0].stack().rename(index) for index, df in dataframes.items()], 
    axis=1).reset_index()
combined_corr_df.columns = ['Region', 'Month'] + list(dataframes.keys())

# Combine all p-values into one DataFrame
combined_pval_df = pd.concat(
    [df[1].stack().rename(index) for index, df in dataframes.items()], 
    axis=1).reset_index()
combined_pval_df.columns = ['Region', 'Month'] + list(dataframes.keys())

# Plot the heatmap for correlation coefficients
plt.figure(figsize=(20, 12))
corr_heatmap_data = combined_corr_df.pivot('Region', 'Month', 'enso')
for col in combined_corr_df.columns[2:]:
    corr_heatmap_data += combined_corr_df.pivot('Region', 'Month', col)
corr_heatmap_data /= len(combined_corr_df.columns[2:])

sns.heatmap(corr_heatmap_data, annot=True, cmap='coolwarm', center=0, cbar_kws={'label': 'Average Correlation Coefficient'})
plt.title('Average Correlation Coefficients between Antarctic Sea Ice Extent and Climate Indices')
plt.xlabel('Month')
plt.ylabel('Region')
plt.show()

# Plot the heatmap for p-values
plt.figure(figsize=(20, 12))
pval_heatmap_data = combined_pval_df.pivot('Region', 'Month', 'enso')
for col in combined_pval_df.columns[2:]:
    pval_heatmap_data += combined_pval_df.pivot('Region', 'Month', col)
pval_heatmap_data /= len(combined_pval_df.columns[2:])

sns.heatmap(pval_heatmap_data, annot=True, cmap='viridis_r', cbar_kws={'label': 'Average p-value'})
plt.title('Average p-values for Correlations with Climate Indices')
plt.xlabel('Month')
plt.ylabel('Region')
plt.show()