import folium
import numpy as np
from folium.plugins import HeatMap, MarkerCluster

def add_decade_heat_layers(m, df):
    # grouping quakes by decade so we can toggle each one separately
    if "year" not in df.columns: return
    df["decade"] = (df["year"] // 10) * 10
    for d, chunk in df.groupby("decade"):
        pts = chunk[["lat","lon","mag"]].dropna().to_numpy()
        if len(pts) == 0: continue
        pts = np.column_stack([pts[:,0], pts[:,1], np.clip(pts[:,2], 0.0, 7.0)]).tolist()
        HeatMap(pts, radius=10, blur=12, min_opacity=0.35, name=f"{d}s (Heat)").add_to(m)

def add_magbin_markers(m, df):
    # making marker clusters for each magnitude range (so it’s easier to compare)
    if "mag_bin" not in df.columns: return
    for label, chunk in df.groupby("mag_bin", dropna=True):
        mc = MarkerCluster(name=f"Mag {label}").add_to(m)
        # adds small circle markers for each quake in that magnitude group
        for _, r in chunk.iterrows():
            folium.CircleMarker([r["lat"], r["lon"]],
                radius=3, weight=0.5, fill=True, fill_opacity=0.7).add_to(mc)
