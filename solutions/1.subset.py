# imports
import geopandas as gpd
from os.path import normpath, join, isfile


# file locations
DATA_DIR = normpath("D:/glintsolar/data/")
path_to_parcels = join(DATA_DIR, "Cadastral Parcels/NSD_merged.geojson")
path_to_wards = join(DATA_DIR, "wards_cropped.geojson")
path_for_output = join(DATA_DIR, "RefinedData/NSD_peeled.geojson")


if isfile(path_to_parcels) and isfile(path_to_wards):
    # reading the GeoJSON with wards and selecting only needed
    wards = gpd.read_file(path_to_wards, layer="WD_MAY_2024_UK_BFC", where="WD24NM != 'Loddon & Chedgrave'")
    # merging all wards into one GeoSeries
    # https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoSeries.union_all.html#geopandas.GeoSeries.union_all
    wards_union = wards.union_all(method="unary")

    # reading the GeoJSON with parcels
    parcels = gpd.read_file(path_to_parcels, layer="merged")

    # subset of parcels where its areas are equal or more than 1 hectare
    # 1 hectare is equal to 10.000 m²
    parcels_filtered = parcels[parcels.geometry.area / 10000 >= 1]

    # converting parcels geometries from polygons to points using the representative_point method
    # https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoSeries.representative_point.html
    parcels_filtered_repr = parcels_filtered.copy()
    parcels_filtered_repr = parcels_filtered_repr.set_geometry(parcels_filtered_repr.representative_point())

    # getting a subset of parcels' representative points that are within specified wards
    parcels_filtered_repr = parcels_filtered_repr[parcels_filtered_repr.geometry.within(wards_union, align=True)]

    # getting a subset of parcels that are within specified wards
    parcels_peeled = parcels_filtered[parcels_filtered.index.isin(parcels_filtered_repr.index.to_list())]
    # exporting the final result
    parcels_peeled.to_file(path_for_output, driver="GeoJSON", layer="parcels")
