import folium
import numpy as np
from folium.plugins import HeatMap, MarkerCluster

def add_decade_heat_layers(m, df):
    # grouping quakes by decade so we can toggle each one separately
    # Only show the most recent decade by default for cleaner initial view
    if "year" not in df.columns: return
    df["decade"] = (df["year"] // 10) * 10
    decades = sorted(df["decade"].unique(), reverse=True)

    for i, d in enumerate(decades):
        chunk = df[df["decade"] == d]
        pts = chunk[["lat","lon","mag"]].dropna().to_numpy()
        if len(pts) == 0: continue
        pts = np.column_stack([pts[:,0], pts[:,1], np.clip(pts[:,2], 0.0, 7.0)]).tolist()

        # Show only the most recent decade by default (i == 0)
        show_layer = (i == 0)
        HeatMap(
            pts,
            radius=10,
            blur=12,
            min_opacity=0.35,
            name=f"Decade: {d}s",
            show=show_layer,
            overlay=True,
            control=True
        ).add_to(m)

def add_magbin_markers(m, df, sample_limit=None):
    # making marker clusters for each magnitude range (so it's easier to compare)
    # sample_limit: optional max markers per bin (e.g., 500) for performance
    if "mag_bin" not in df.columns: return
    for label, chunk in df.groupby("mag_bin", dropna=True):
        mc = MarkerCluster(name=f"Mag {label}").add_to(m)

        # Sample if needed (keeps larger magnitudes, samples smaller ones)
        if sample_limit and len(chunk) > sample_limit:
            # For small magnitudes (lots of data), sample intelligently
            chunk = chunk.sample(n=sample_limit, random_state=42)

        # adds small circle markers for each quake in that magnitude group
        for _, r in chunk.iterrows():
            folium.CircleMarker([r["lat"], r["lon"]],
                radius=3, weight=0.5, fill=True, fill_opacity=0.7).add_to(mc)
