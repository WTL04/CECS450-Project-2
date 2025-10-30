import folium
import pandas as pd
import geopandas as gpd
from folium.plugins import HeatMap


# population data preprocessing
df = pd.read_csv("datasets/MCNA_-_Population_Points_with_T_D_Standards.csv")

# drop unessesary columns
df.drop(columns=[
    "CENSUS_TRACT",
    "CENSUS_BLOCK_GROUP",
    "ALL_PLAN",
    "County_Size_Type",
    "Loc_Code_Gcode"
], axis=1, inplace=True)

for col in df.columns:
    if "DT" in col or "TT" in col:
        df.drop(col, axis=1, inplace=True)

# turn long lang into geometries
geometry = geopandas.points_from_xy(df.LONGITUDE, df.LATITUDE)
geo_df = geopandas.GeoDataFrame(
    df, geometry=geometry, crs="EPSG:4326"
)

# clear N/A values
geo_df = geo_df.dropna(subset=["LATITUDE", "LONGITUDE"])


# set up map layers
center = (37.301104, -119.721280) # center of cali
m = folium.Map(location=center, zoom_start=6)

# fault line layer
folium.raster_layers.TileLayer(
    tiles="https://gis.conservation.ca.gov/server/rest/services/CGS/FaultActivityMapCA/MapServer/tile/{z}/{y}/{x}",
    name="CGS Faults (toggle)",
    attr="California Geological Survey",
    overlay=True, control=True,
    show=True,          # show fault lines
    max_zoom=14, opacity=0.9
).add_to(m)

# heatmap layer
heat_data = [[pt.y, pt.x] for pt in geo_df.geometry]
HeatMap(
    heat_data,
    name="Population heat",
    radius=12,
    blur=18,
    min_opacity=0.25,
    max_zoom=12,
    show=True,          # make it visible initially
    control=True
).add_to(m)