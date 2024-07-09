# What is this?
Repo to store my python code files, data and other misc stuff like results and reports for my work at National Centre for Polar and Ocean Research (NCPOR, erstwhile NCAOR) in Polar Remote Sensing, Earth Sciences under Dr. Alvarinho J. Luis for Practice School - I, BITS Pilani (FIC - Dr. Sunari R.)

# MidSem report
I compiled the report using LaTeX. Chapters 3 and 4 are my the majority of my contributions.

- Presentation: [ps_presentation.pdf](https://drive.google.com/file/d/1pyE9YA5bnL0Kn0xeJJamyAHNN2el2b8i/view)
- Report: [ps_midsem_report.pdf](https://drive.google.com/file/d/1vboyDBEHo3QAc9uCUEVktUz7bMdnTSCz/view)

# Data Used
- https://noaadata.apps.nsidc.org
- https://www.weather.gov/fwd/indices
- https://psl.noaa.gov/pdo/
- https://psl.noaa.gov/gcos_wgsp/Timeseries/DMI/
- https://doi.org/10.24381/cds.f17050d7

# Glossary
<dl>
  <dt><b>SIE</b></dt><dd>Sea Ice Extent</dd>
  <dt><b>ENSO</b></dt><dd>El Niño-Southern Oscillation</dd>
  <dt><b>PDO</b></dt><dd>Pacific Decadal Oscillation</dd>
  <dt><b>ERA</b></dt><dd>ECMWF Re-Analysis Data, 5<sup>th</sup> generation</dd>
  <dt><b>SST</b></dt><dd>Sea Surface Temperature</dd>
  <dt><b>SSR</b></dt><dd>Surface Short-wave Solar Radiation</dd>
  <dt><b>SSR</b></dt><dd>Surface Long-wave Thermal Radiation</dd>
  <dt><b>IOD</b></dt><dd>Indian Ocean Dipole</dd>
  <dt><b>DMI</b></dt><dd>Dipole Mode Index</dd>
  <dt><b>SAM</b></dt><dd>Southern Annular Mode</dd>
  <dt><b>SLHF</b></dt><dd>Surface Latent Heat Flux</dd>
  <dt><b>SSHF</b></dt><dd>Surface Sensible Heat Flux</dd>
  <dt><b>NOAA</b></dt><dd>National Oceanic and Atmospheric Administration</dd>
  <dt><b>NSIDC</b></dt><dd>National Snow and Ice Data Center</dd>
</dl>

# CDO command for future ref
/home/march/NCPOR/software/CDO/cdo-2.4.1/src/cdo outputtab,date,lat,lon,value adaptor.mars.internal.nc > out.csv