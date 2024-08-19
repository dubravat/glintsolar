# imports
import geopandas as gpd
from os.path import normpath, join, isfile
from folium import Map, Element
from folium.features import GeoJson, GeoJsonTooltip
from folium.plugins import Fullscreen
from folium.map import LayerControl

# file locations
PROJECT_DIR = normpath("D:/glintsolar/")
path_to_parcels = join(PROJECT_DIR, "data/RefinedData/NSD_joined.geojson")
visual_output = join(PROJECT_DIR, "solutions/3.map.folium.html")


# initiating a Leaflet Map
m = Map(tiles='CartoDB Positron', left='5%', width='90%', height='90%', zoom_start=9)
# adding a title
title = '<h1 align="center" style="font-size:16px">Parcels owned by foreign and domestic companies</h1>'
m.get_root().html.add_child(Element(title))

if isfile(path_to_parcels):
    # reading the GeoJSON with parcels
    parcels = gpd.read_file(path_to_parcels, layer="parcels")
    # reprojecting to EPSG:4326
    parcels = parcels.to_crs(epsg=4326)

    # handling MultiPolygon geometries, otherwise the UserWarning:
    # GeoJsonTooltip is not configured to render for GeoJson GeometryCollection geometries.
    # Please consider reworking these features:
    # [{'origin': 'NSD_CLIPPED7_LR_POLY_FULL_AUG_2024_7', 'POLY_ID': 40555188, ...}]
    # to MultiPolygon for full functionality.
    # https://tools.ietf.org/html/rfc7946#page-9:
    parcels = parcels.explode()

    # setting a map center location
    # https://gis.stackexchange.com/questions/372564/userwarning-when-trying-to-get-centroid-from-a-polygon-geopandas
    parcels_center = parcels.to_crs('+proj=cea').dissolve().geometry.centroid.to_crs(parcels.crs).loc[0]
    m.location = [parcels_center.y, parcels_center.x]

    # treating some columns as text, to avoid the TypeError: Object of type Timestamp is not JSON serializable
    parcels['INSERT'], parcels['UPDATE'] = parcels['INSERT'].astype(str), parcels['UPDATE'].astype(str)

    # getting a list of all fields inside the GeoJSON
    fields = parcels.drop(columns="geometry").columns.tolist()

    # calling the GeoJson class to set up and visualize a GeoDataFrame
    # https://gis.stackexchange.com/questions/445020/highlight-geometry-in-folium-map-on-hover
    parcels_layer = GeoJson(
        data=parcels,
        name='parcels',
        style_function=lambda feat: {'color': '#FFFFFF', 'fillColor': '#00205B', 'weight': 2.0, 'opacity': 0.5, 'fillOpacity': 0.6},
        highlight_function=lambda feat: {'color': '#BA0C2F', 'fillOpacity': 0.2},
        tooltip=GeoJsonTooltip(fields=fields, style="background-color: #FEEFF2; color: #333333; font-family: arial; font-size: 10px; padding: 8px;")
    )

    # adding a GeoJson object to the map
    parcels_layer.add_to(m)

    # adding the full screen control button
    Fullscreen().add_to(m)
    LayerControl(position='topright', collapsed=False, autoZIndex=True).add_to(m)

    # finding parcels' bounds
    bounds = parcels.total_bounds  # minx, miny, maxx, maxy
    bounds = list(map(lambda x: float(x), bounds))  # converting numpy to float
    bounds = [[bounds[1], bounds[0]], [bounds[3], bounds[2]]] # [[south, west], [north, east]]
    # adjusting map's zoom level based on parcels' bounds
    # https://python-visualization.github.io/folium/latest/reference.html#folium.folium.Map.fit_bounds
    # The lat/lon bounds in the form (list of (latitude, longitude) points)
    m.fit_bounds(bounds)


if __name__ == '__main__':
     m.save(outfile=visual_output, title='Norwich Parcels')
