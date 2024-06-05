import pandas as pd
import numpy as np
import scipy.signal as signal

# Define the year range, regions, and relative path to the data
year_list = list(range(1979, 2024))
regions = ["Bell-Amundsen", "Indian", "Pacific", "Ross", "Weddell"]
rel_path = "../../data/"

# Define the number of days in each month for averaging purposes
month_days = {
    "January": 31,
    "February": 29,
    "March": 31,
    "April": 30,
    "May": 31,
    "June": 30,
    "July": 31,
    "August": 31,
    "September": 30,
    "October": 31,
    "November": 30,
    "December": 31
}

# Define a function to process and filter sea ice data for a given region
def process_sea_ice_data(region):
    # Load the sea ice extent data from Excel
    excel_path = rel_path + "S_Sea_Ice_Index_Regional_Daily_Data_G02135_v3.0.xlsx"
    df_sea_ice = pd.read_excel(excel_path, sheet_name=region + "-Extent-km^2")
    df_sea_ice.drop(df_sea_ice.columns[[-1, 0, 1, 2]], axis=1, inplace=True)

    # Flatten the data and interpolate missing values
    extent = pd.Series(df_sea_ice.values.ravel()).astype(float)
    extent.interpolate(method='linear', inplace=True)

    # Apply the Butterworth filter
    N = 2  # Filter order
    Wn = 0.6  # Cutoff frequency (normalized from 0 to 1)
    B, A = signal.butter(N, Wn, output='ba')
    extent_filtered = pd.Series(signal.filtfilt(B, A, extent))

    # Create a DataFrame with dates for grouping
    dates = pd.date_range(start='1979-01-01', periods=len(extent_filtered), freq='D')
    df_filtered = pd.DataFrame({'Date': dates, 'Extent': extent_filtered})

    # Calculate the monthly average extent
    df_filtered.set_index('Date', inplace=True)
    monthly_average = df_filtered.resample('M').mean()

    return monthly_average

# Process and filter data for each region
monthly_averages = {}
for region in regions:
    monthly_averages[region] = process_sea_ice_data(region)

print(monthly_averages)

# Example of how to access and plot the monthly averages for a specific region
# import matplotlib.pyplot as plt

# region_to_plot = 'Bell-Amundsen'
# monthly_avg = monthly_averages[region_to_plot]

# plt.figure(figsize=(10, 5))
# plt.plot(monthly_avg.index, monthly_avg['Extent'], label=region_to_plot)
# plt.xlabel('Year')
# plt.ylabel('Sea Ice Extent (km^2)')
# plt.title(f'Monthly Averaged Sea Ice Extent - {region_to_plot}')
# plt.legend()
# plt.show()