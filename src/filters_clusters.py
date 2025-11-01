import pandas as pd
from folium.plugins import HeatMap
from src.filters_magnitude import add_magnitude_layers
from src.filters_depth import add_depth_layers
from src.filters_region import add_region_layers


def add_filtered_layers(m, df):
    df = df.copy()
    df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
    df["year"] = df["datetime"].dt.year
    df["depth"] = pd.to_numeric(df["depth"], errors="coerce").fillna(0)
    df["mag"] = pd.to_numeric(df["mag"], errors="coerce")
    df = df.dropna(subset=["lat", "lon", "mag", "datetime"])
    df = df[(df["lat"].between(32, 36)) & (df["lon"].between(-120, -114))]

    print(f"Loaded {len(df)} SoCal earthquakes")

    heat_data = [[r.lat, r.lon, r.mag] for _, r in df.iterrows()]
    HeatMap(heat_data, radius=10, blur=15, name="Heatmap (All SoCal Events)").add_to(m)
    add_magnitude_layers(m, df)
    add_depth_layers(m, df)
    add_region_layers(m, df)

    print("Added all SoCal layers (county-based)")

