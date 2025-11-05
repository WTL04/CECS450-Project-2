# src/time_slider.py
def add_time_slider_layer(m, df, mag_min=5.0):
    from folium.plugins import TimestampedGeoJson
    import pandas as pd

    # 1) find time
    time_cols = ["time", "origintimeUTC", "datetime", "event_time", "Date", "date"]
    time_col = next((c for c in time_cols if c in df.columns), None)

    if time_col is not None:
        tmp = df.dropna(subset=["lat", "lon", time_col]).copy()
        tmp[time_col] = pd.to_datetime(tmp[time_col], errors="coerce")
        tmp = tmp[tmp[time_col].notna()]
        tmp["__year"] = tmp[time_col].dt.year
    else:
        if "year" not in df.columns:
            raise KeyError("No time-like column and no 'year' column found.")
        tmp = df.dropna(subset=["lat", "lon", "year"]).copy()
        tmp["__year"] = tmp["year"].astype(int)

    # 2) keep only mag >= mag_min (configurable, default 5.0 for performance)
    mag_col_exists = "mag" in tmp.columns
    if mag_col_exists:
        tmp = tmp[tmp["mag"] >= mag_min]

    # 3) sort + years
    tmp = tmp.sort_values("__year")
    years = sorted(tmp["__year"].unique().tolist())

    all_features = []

    # helper to get style - MATCHES unified layer visual encoding
    # SIZE = magnitude, COLOR = depth (green/orange/purple)
    def get_style(mag_val: float, depth_val: float):
        # Magnitude-based sizing (MATCHES unified layer exactly)
        if mag_val >= 7.0:
            radius = 35  # Massive - unmissable!
        elif mag_val >= 6.0:
            radius = 25  # Very large
        elif mag_val >= 5.0:
            radius = 18  # Large
        elif mag_val >= 4.0:
            radius = 12  # Medium
        else:
            radius = 8   # Small but still visible

        # Depth-based coloring (adjusted for California's shallow crustal geology)
        if depth_val < 10:
            color = "#50c878"  # Green - very shallow
        elif depth_val < 20:
            color = "#ff8c00"  # Orange - shallow
        else:
            color = "#9b59b6"  # Purple - deeper

        return {"color": color, "radius": radius}

    # FIXED: Create one feature per earthquake (non-cumulative) to avoid exponential data growth
    # Each earthquake appears once at its actual timestamp
    for _, r in tmp.iterrows():
        year = int(r["__year"])
        mag_val = float(r["mag"]) if (mag_col_exists and not pd.isna(r["mag"])) else 5.0
        depth_val = float(r["depth"]) if not pd.isna(r["depth"]) else 0.0

        s = get_style(mag_val, depth_val)

        all_features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [float(r["lon"]), float(r["lat"])],
            },
            "properties": {
                "time": f"{year:04d}-01-01T00:00:00",
                "icon": "circle",
                "iconstyle": {
                    "fillOpacity": 0.4,  # Reduced from 0.7 to be less distracting
                    "stroke": "true",
                    "color": s["color"],     # outline
                    "fillColor": s["color"], # fill
                    "radius": s["radius"],
                    "weight": 1  # Thinner outline
                },
            },
        })

    # Add time slider directly to map (plugin limitation - cannot be wrapped in FeatureGroup)
    TimestampedGeoJson(
        {"type": "FeatureCollection", "features": all_features},
        period="P1Y",
        add_last_point=True,
        auto_play=False,
        loop_button=True,
        date_options="YYYY",
        time_slider_drag_update=True,
        duration="P1Y",
    ).add_to(m)

    print(f"Time slider: {len(tmp)} earthquakes from {min(years)} to {max(years)}")
    print("Note: Time slider is always active (plugin limitation - cannot be toggled off)")
