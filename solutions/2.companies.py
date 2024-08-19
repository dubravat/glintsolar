# imports
import pandas as pd
import geopandas as gpd
from shapely import make_valid
from os.path import normpath, join, isfile


# file locations
PROJECT_DIR = normpath("D:/glintsolar/")
path_to_ccod = join(PROJECT_DIR, "data/Companies that own land/CCOD.csv")  # bigger
path_to_ocod = join(PROJECT_DIR, "data/Companies that own land/OCOD.csv")  # smaller
path_to_parcels = join(PROJECT_DIR, "data/RefinedData/NSD_peeled.geojson")


if isfile(path_to_ccod) and isfile(path_to_ocod) and isfile(path_to_parcels):
    # reading the CSV with domestic companies
    domestic_comps = pd.read_csv(path_to_ccod, sep=',', engine='python', encoding='utf8')
    # reading the CSV with foreign companies
    foreign_comps = pd.read_csv(path_to_ocod, sep=',', engine='python', encoding='utf8')

    # extracting only companies in required counties and districts
    expr = "County != 'SURREY' & District in ['EAST SUFFOLK', 'SOUTH NORFOLK']"
    domestic_comps_clean = domestic_comps.query(expr)  # There are NO duplicates in "Title Number" field
    foreign_comps_clean = foreign_comps.query(expr)  # There are NO duplicates in "Title Number" field

    # reading the GeoJSON with parcels
    parcels = gpd.read_file(path_to_parcels, layer="parcels")  # There are duplicates in "TITLE_NO" field
    # performing some geometries manipulations
    parcels.geometry.normalize()
    parcels.geometry = parcels.apply(
        lambda row: make_valid(row.geometry) if not row.geometry.is_valid else row.geometry, axis=1)

    # getting a subset of columns in each data set
    some_fields = [
        "Title Number", "Tenure",
        "Proprietor Name (1)", "Proprietor Name (2)", "Proprietor Name (3)", "Proprietor Name (4)"
    ]
    domestic_comps_clean = domestic_comps_clean[some_fields]
    foreign_comps_clean = foreign_comps_clean[some_fields]

    # adding prefixes before joins
    domestic_comps_clean = domestic_comps_clean.add_prefix('dom_')
    foreign_comps_clean = foreign_comps_clean.add_prefix('for_')

    # joining domestic and foreign companies to parcels i.e. one-to-many
    parcels = parcels.merge(domestic_comps_clean, how='left', left_on='TITLE_NO', right_on='dom_Title Number',
                            suffixes=('', ''), validate="many_to_one")
    parcels = parcels.merge(foreign_comps_clean, how='left', left_on='TITLE_NO', right_on='for_Title Number',
                            suffixes=('', ''), validate="many_to_one")

    # exporting the final result
    parcels.to_file(join(PROJECT_DIR, "data/RefinedData/NSD_joined.geojson"), driver="GeoJSON", layer="parcels")
