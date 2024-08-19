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
path_to_generation_headroom = join(PROJECT_DIR, "data/generation_headroom_.geojson")
path_to_aonb = join(PROJECT_DIR, "data/Areas_of_Outstanding_Natural_Beauty_England.json")
visual_output = join(PROJECT_DIR, "solutions/4.map.folium.html")


# initiating a Leaflet Map
m = Map(tiles='CartoDB Positron', left='5%', width='90%', height='90%')
# adding a title
title = '<h1 align="center" style="font-size:16px">Best parcels to build a utility-scale solar park</h1>'
m.get_root().html.add_child(Element(title))


if isfile(path_to_parcels) and isfile(path_to_generation_headroom) and isfile(path_to_aonb):
    # reading the GeoJSON with generation headroom
    headroom = gpd.read_file(path_to_generation_headroom, layer="dfes-network-headroom-report", where="category = 'Demand Headroom'")
    # performing some geometries manipulations
    headroom.geometry = headroom.normalize()
    headroom.drop_duplicates()
    # getting a sum of 'headroom' per each 'gridsupplypoint'
    headroom_agg = headroom.groupby(by=['gridsupplypoint'], as_index=False, sort=False).agg({'headroom': 'sum'})
    headroom_agg = headroom_agg[headroom_agg['headroom'] > 0]  # consider only positive values
    # erasing empty geometries
    headroom = headroom[~headroom.is_empty]
    # getting the first feature after grouping by geometry
    headroom = headroom.groupby('geometry', as_index=False).first()
    # extracting only features with positive headroom
    headroom = headroom[headroom['gridsupplypoint'].isin(headroom_agg['gridsupplypoint'].values)]
    # converting DataFrame to GeoDataFrame
    headroom = gpd.GeoDataFrame(headroom, geometry="geometry")

    # reading the GeoJSON with Areas of Outstanding Natural Beauty England
    natural_beauty = gpd.read_file(path_to_aonb)
    natural_beauty = natural_beauty.to_crs(epsg=27700)

    # reading the GeoJSON with parcels
    parcels = gpd.read_file(path_to_parcels, layer="parcels")

    # extracting only closest parcels to generation headroom
    parcels_close_headroom = gpd.sjoin_nearest(parcels, headroom, how='left', max_distance=3000, lsuffix='', rsuffix='_', distance_col="dist")
    parcels_close_headroom = parcels_close_headroom[parcels_close_headroom["dist"].notna()]

    # treating some columns as text, to avoid the TypeError: Object of type Timestamp is not JSON serializable
    parcels_close_headroom['INSERT'] = parcels_close_headroom['INSERT'].astype(str)
    parcels_close_headroom['UPDATE'] = parcels_close_headroom['UPDATE'].astype(str)

    # excluding areas that overlap with outstanding natural beauty
    parcels_no_natural_beauty = gpd.overlay(parcels_close_headroom, natural_beauty, how='difference') # 5806 rows

    # filtering only parcels owned by companies
    expr = "dom_Tenure == 'Freehold' | for_Tenure == 'Freehold'"
    parcels_filtered = parcels_no_natural_beauty.query(expr)

    # filtering only parcels owned by one company
    needed_fields = list(filter(lambda x: 'Proprietor Name' in x, parcels_filtered.columns.to_list()))
    parcels_filtered_subset = parcels_filtered[needed_fields]
    parcels_one_owner = parcels_filtered[parcels_filtered_subset.apply(lambda row: sum(x is not None for x in row.values) == 1, axis=1)]
    parcels_one_owner = parcels_one_owner.to_crs(epsg=4326)

    # getting a list of all fields inside the GeoJSON
    fields = parcels_one_owner.drop(columns="geometry").columns.tolist()

    # calling the GeoJson class to set up and visualize a GeoDataFrame
    # https://gis.stackexchange.com/questions/445020/highlight-geometry-in-folium-map-on-hover
    parcels_layer = GeoJson(
        data=parcels_one_owner,
        name='best parcels',
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
    bounds = parcels_one_owner.total_bounds  # minx, miny, maxx, maxy
    bounds = list(map(lambda x: float(x), bounds))  # converting numpy to float
    bounds = [[bounds[1], bounds[0]], [bounds[3], bounds[2]]] # [[south, west], [north, east]]
    # adjusting map's zoom level based on parcels' bounds
    # https://python-visualization.github.io/folium/latest/reference.html#folium.folium.Map.fit_bounds
    # The lat/lon bounds in the form (list of (latitude, longitude) points)
    m.fit_bounds(bounds)

if __name__ == '__main__':
     m.save(outfile=visual_output, title='Norwich Best Parcels')
