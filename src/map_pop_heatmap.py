import folium
import geopandas
from folium.plugins import HeatMap


def add_pop_heatmap(m, df_pop):
    # drop unessesary columns
    df_pop.drop(
        columns=[
            "CENSUS_TRACT",
            "CENSUS_BLOCK_GROUP",
            "ALL_PLAN",
            "County_Size_Type",
            "Loc_Code_Gcode",
        ],
        axis=1,
        inplace=True,
    )

    for col in df_pop.columns:
        if "DT" in col or "TT" in col:
            df_pop.drop(col, axis=1, inplace=True)

    #   turn long lang into geometries
    geometry = geopandas.points_from_xy(df_pop.LONGITUDE, df_pop.LATITUDE)
    geo_df = geopandas.GeoDataFrame(df_pop, geometry=geometry, crs="EPSG:4326")

    # clear N/A values
    geo_df = geo_df.dropna(subset=["LATITUDE", "LONGITUDE"])

    # heatmap layer
    heat_data = [[pt.y, pt.x] for pt in geo_df.geometry]
    HeatMap(
        heat_data,
        name="Context: Population Density",
        radius=12,
        blur=18,
        min_opacity=0.25,
        max_zoom=12,
        show=False,  # hidden by default (toggle on when needed)
        control=True,
        overlay=True,
    ).add_to(m)

    print("Added population heatmap layer to California")
