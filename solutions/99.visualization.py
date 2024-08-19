# imports
import geopandas as gpd
from os.path import normpath, join, isfile
from ipyleaflet import Map, GeoData, Polygon, basemaps, basemap_to_tiles, LayersControl, FullScreenControl, Popup, Marker
from ipywidgets import HTML
from shapely.geometry import shape, mapping
from pyproj import Geod

# file locations
PROJECT_DIR = normpath("D:/glintsolar/")
path_to_parcels = join(PROJECT_DIR, "data/RefinedData/NSD_joined_mini.geojson")
visual_output = join(PROJECT_DIR, "solutions/99.map.ipyleaflet.html")


# initiating a Leaflet Map
m = Map(basemap=basemap_to_tiles(basemaps.CartoDB.Positron))
m.layout.width, m.layout.height = '1400px', '800px'
m.scroll_wheel_zoom = True
m.box_zoom = False

def on_click(event, feature, **kwargs):
    html_widget = HTML(placeholder="", description="")
    html_widget.value = f"<strong>{feature['properties']}</strong>"
    coords = shape(feature.geometry).representative_point()

    # creating the popup
    popup = Popup(
        location=[coords.y, coords.x],
        child=html_widget,
        max_width=300,
        close_button=True,
        close_on_escape_key=True,
        auto_close=True,
    )
    m.add(popup)

if isfile(path_to_parcels):
    # reading the GeoJSON with parcels
    parcels = gpd.read_file(path_to_parcels, layer="parcels")
    # reprojecting to EPSG:4326
    parcels = parcels.to_crs(epsg=4326)

    # setting a map center
    # https://gis.stackexchange.com/questions/372564/userwarning-when-trying-to-get-centroid-from-a-polygon-geopandas
    parcels_center = parcels.to_crs('+proj=cea').dissolve().geometry.centroid.to_crs(parcels.crs).loc[0]
    m.center = [parcels_center.y, parcels_center.x]

    # treating some columns as text, to avoid the TypeError: Object of type Timestamp is not JSON serializable
    parcels['INSERT'], parcels['UPDATE'] = parcels['INSERT'].astype(str), parcels['UPDATE'].astype(str)

    # calling the GeoData class to visualize a GeoDataFrame
    parcels_layer = GeoData(
        geo_dataframe=parcels,
        style={'color': '#FFFFFF', 'fillColor': '#00205B', 'weight': 2.0, 'opacity': 0.5, 'fillOpacity': 0.6},
        hover_style={'color': '#BA0C2F', 'fillOpacity': 0.2},
        name='parcels'
    )
    m.add(parcels_layer)

    parcels_layer.on_click(callback=on_click, remove=False)

    # adding the full screen control button
    m.add(FullScreenControl())
    m.add(LayersControl(position='topright'))

    # finding parcels' bounds
    bounds = parcels.total_bounds  # minx, miny, maxx, maxy
    bounds = list(map(lambda x: float(x), bounds))
    bounds = [[bounds[1], bounds[0]], [bounds[3], bounds[2]]]
    # adjusting map's zoom level based on parcels' bounds
    # The lat/lon bounds in the form [[south, west], [north, east]]
    # east, west, north, south = lon, lon, lat, lat
    m.fit_bounds(bounds)


if __name__ == '__main__':
     m.save(outfile=visual_output, title='Norwich Parcels')
