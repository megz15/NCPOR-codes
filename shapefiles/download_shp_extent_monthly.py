from requests import get
import os

months = [
    "01_Jan", "02_Feb", "03_Mar", 
    "04_Apr", "05_May", "06_Jun",
    "07_Jul", "08_Aug", "09_Sep", 
    "10_Oct", "11_Nov", "12_Dec",
]

years = list(range(1979, 2024))
rel_path = "shapefiles/data/"

for month in months:
    
    save_folder = rel_path + month
    os.makedirs(save_folder, exist_ok=True)
    
    for year in years:

        file_name = f"extent_S_{year}01_polygon_v3.0.zip"
        file_path = os.path.join(save_folder, file_name)

        url = f"https://noaadata.apps.nsidc.org/NOAA/G02135/south/monthly/shapefiles/shp_extent/{month}/{file_name}"

        r = get(url)

        if r.status_code == 200:
            with open(file_path, 'wb') as file:
                file.write(r.content)
            print(f"{file_path} OK")
        else:
            print(f"{file_path} FAIL: {r.status_code}")

    print(f"\n{month} DONE\n")