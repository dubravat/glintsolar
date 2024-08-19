# Job Application as GIS Specialist at GlintSolar
## (C) Taras Dubrava
### July 2024

----

## Attempts to accomplish the Take Home Case

### I. Input data examination and preparation
   
   1. Exploring the input
      
      Input files:
      ```cmd
      data
      │   generation_headroom.geojson
      │   wards_cropped.geojson
      │
      ├───Cadastral Parcels
      │       NSD_CLIPPED0.geojson
      │       NSD_CLIPPED1.geojson
      │       NSD_CLIPPED2.geojson
      │       NSD_CLIPPED3.geojson
      │       NSD_CLIPPED4.geojson
      │       NSD_CLIPPED5.geojson
      │       NSD_CLIPPED6.geojson
      │       NSD_CLIPPED7.geojson
      │       NSD_CLIPPED8.geojson
      │       NSD_CLIPPED9.geojson
      │
      └───Companies that own land
              CCOD.csv
              OCOD.csv
      ```
      Input files:
         - GeoJSON : 12 files
         - CSV : 2 elements
   
      Checking the EPSG of the GeoJSON files
      ```cmd
      > for /R %f in (*.geojson) do gdalsrsinfo -e "%f"| find "EPSG:"
      ```
   
      All files are in [EPSG:27700](https://epsg.org/crs_27700/OSGB36-British-National-Grid.html), besides
the `generation_headroom.geojson` which is in [EPSG:4326](https://epsg.org/crs_4326/WGS-84.html).

   2. Merging all GeoJSON in the `Cadastral Parcels` dir
   
      ```cmd
      > ogrmerge -f "GeoJSON" -single -src_layer_field_name "origin" -o NSD_merged.geojson *.geojson
      ```
   
   3. Reprojecting the `generation_headroom` into `EPSG:27700`
      ```cmd
      > ogr2ogr -s_srs EPSG:4326 -t_srs EPSG:27700 -f "GeoJSON" generation_headroom_.geojson generation_headroom.geojson
      ```
      
   Usually the OSGeo4W shell could be found under the `C:\OSGeo4W`.

   *Used tools and software:*
   - [`gdalsrsinfo`](https://gdal.org/programs/gdalsrsinfo.html)
   - [`ogrmerge`](https://gdal.org/programs/ogrmerge.html)
   - [`ogr2ogr`](https://gdal.org/programs/ogr2ogr.html)
   - QGIS 3.34.8-Prizren

### II. Data processing, filtering, and rectification
   
   Input file: `NSD_merged.geojson`</br>
   Solution: [`1.subset.py`](solutions/1.subset.py)</br>
   Input file: `NSD_peeled.geojson`</br>

   *Used tools, software and packages:*
   - Python 3.11 in PyCharm 2023.2.1 (Community Edition)
   - `geopandas`, `os.path`
   - QGIS 3.34.8-Prizren

### III. Companies

   Input files:</br>
       - `NSD_peeled.geojson`</br>
       -  `CCOD.csv`</br>
       -  `OCOD.csv`</br>
   Solution: [`2.companies.py`](solutions/2.companies.py)</br>
   Output file: `NSD_joined.geojson`</br>
      
   1. *CCOD:* UK companies that own property in England and Wales 
   2. *OCOD:* Overseas companies that own property in England and Wales

   Working area:
   - Counties: SUFFOLK, NORFOLK
   - Districts: EAST SUFFOLK, SOUTH NORFOLK

   *Used extra data*:
   - [GeoPackage | GB Counties - Past and Present](https://www.data.gov.uk/dataset/c532a556-c36c-45aa-a57e-2d73930f9776/gb-counties-past-and-present)
   
   *Used tools, services, software and packages:*
   - Python 3.11 in PyCharm 2023.2.1 (Community Edition)
   - `pandas`, `geopandas`, `shapely`, `os.path`
   - QGIS 3.34.8-Prizren
   - <s>[`requests`](https://requests.readthedocs.io/en/latest/)</s>
   - <s>[OS Places API](https://osdatahub.os.uk/docs/places/overview)</s>

### IV. Data visualization

   Input files:</br>
       - `NSD_peeled.geojson`</br>
       - `CCOD.csv`</br>
       - `OCOD.csv`</br>
   Solution: [`3.visualization.py`](solutions/3.visualization.py)</br>
   Output file: [`3.map.folium.html`](solutions/3.map.folium.html)

   *Used tools, software and packages:*
   - Python 3.11 in PyCharm 2023.2.1 (Community Edition)
   - `folium`, `geopandas`, `os.path`
   - Browser

### V. Choosing the best sites and its visualization

   Input files:</br>
       - `generation_headroom_.geojson`</br>
       - `NSD_joined.geojson`</br>
       - `Areas_of_Outstanding_Natural_Beauty_England.json`</br>
   Solution: [`4.best_choice.py`](solutions/4.best_choice.py)</br>
   Output file: [`4.map.folium.html`](solutions/4.map.folium.html`)

   The process of decision-making involves a combination of technical, environmental, economic,
   and regulatory considerations.

   Criteria of the best (efficient and sustainable) sites to build a utility-scale solar park:
   - ***Solar Irradiance:*** Assess the solar irradiance levels, typically measured in kWh/m²/day.
   Areas with higher solar irradiance are more suitable as they can generate more electricity.
   - ***Sunlight Hours:*** Consider the number of sunlight hours per day and per year.
   Locations closer to the equator generally have more consistent sunlight.
   - ***Land Size and Contiguity:*** Utility-scale solar parks require large, contiguous areas.
   The land should be flat or gently sloping to maximize the efficiency of solar panel installation.
   - ***Land Use Classification:*** Check whether the land is zoned for industrial or agricultural use.
   Avoid areas designated for conservation or urban development.
   - ***Soil Conditions:*** The land should have stable soil that can support the installation of solar panels
   and other infrastructure.
   - ***Distance to Grid:*** The site should be close to existing power lines or substations to minimize the cost
   of transmission line construction and energy loss during transmission.
   - ***Grid Capacity:*** Ensure that the local grid can accommodate the additional electricity generated 
   by the solar park.
   - ***Protected Areas:*** Avoid areas with sensitive ecosystems, wildlife habitats, or protected lands like
   national parks or wetlands.
   - ***Water Resources:*** Consider the proximity to water resources, which may be necessary for cooling or
   cleaning panels, though water usage is generally low for solar parks.
   - ***Biodiversity:*** Conduct an environmental impact assessment to ensure minimal disruption to local flora
   and fauna.
   - ***Zoning Laws:*** Ensure the site complies with local, regional, and national zoning regulations.
   - ***Permits and Approvals:*** Obtain the necessary environmental permits and construction approvals.
   - ***Land Ownership:*** Secure land rights and ownership, whether through purchase, lease, or partnership
   with local landowners.
   - ***Land Cost:*** Consider the cost of land acquisition or leasing. Rural areas are generally more affordable than
   urban or suburban locations.
   - ***Incentives and Subsidies:*** Identify any government incentives, subsidies, or tax breaks available for
   renewable energy projects in the area.
   - ***Labor and Construction Costs:*** Evaluate the availability and cost of local labor and materials required
   for construction.
   - ***Transportation Access:*** Ensure the site is accessible by roads or rail for the delivery of equipment,
   construction materials, and maintenance.
   - ***Proximity to Urban Centers:*** Consider the distance to urban centers for ease of access to services, labor,
   and emergency support.
   - ***Temperature Extremes:*** Consider the local climate, including extreme temperatures, which can affect solar
   panel efficiency and lifespan.
   - ***Natural Hazards:*** Evaluate the risk of natural hazards such as hurricanes, tornadoes, floods, or earthquakes.
   - ***Community Impact:*** Assess the potential impact on local communities, including displacement, changes
   in land use, or visual and noise pollution.
   - ***Stakeholder Support:*** Engage with local stakeholders, including residents, businesses, and government
   authorities, to gain support and address concerns.
   - ***Scalability:*** Consider whether the site allows for future expansion if the solar park is successful.
   - ***Operation and Maintenance:*** Evaluate the long-term maintenance requirements and accessibility of the site.

   *Used tools, services, software and packages:*
   - Areas_of_Outstanding_Natural_Beauty_England dataset provided by the Department
for Environment Food & Rural Affairs via [Defra Data Services Platform (DSP)](https://environment.data.gov.uk/explore/0c1ea47f-3c79-47f0-b0ed-094e0a136971?download=true)
   - Python 3.11 in PyCharm 2023.2.1 (Community Edition)
   - `folium`, `geopandas`, `os.path`
   - QGIS 3.34.8-Prizren
   - [ChatGPT](https://chatgpt.com/)

----

### References:
 - [What is the grid demand headroom and generation headroom?](https://www.linkedin.com/pulse/what-grid-demand-headroom-generation-land-solution-specialists-kjfhe/)
 - [The GeoJSON Specification](https://gist.github.com/sgillies/1233327)
 - [FlagColorCodes](https://www.flagcolorcodes.com/norway)
 - <s>[How to Use Mouse Events on Ipyleaflet](https://medium.com/swlh/how-to-use-mouse-events-on-ipyleaflet-4d002097efc0)</s>
