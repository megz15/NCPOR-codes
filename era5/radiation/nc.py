import xarray as xr

regions = {
    'Ross': {'lon': (160, -130)},
    'Bell-Amundsen': {'lon': (-130, -60)},
    'Weddell': {'lon': (-60, 20)},
    'Indian': {'lon': (20, 90)},
    'Pacific': {'lon': (90, 160)}
}

rel_path = "../../data/"
file_path = rel_path + "netcdf/rad/radiation_1979-2023_monthly_seaice.nc"

with xr.open_dataset(file_path) as ds:
    print(ds["str"].sel(longitude = slice(*regions['Ross']['lon'])))