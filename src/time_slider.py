# src/time_slider.py
def add_time_slider_layer(m, df):
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

    # 2) keep only mag >= 4.0
    mag_col_exists = "mag" in tmp.columns
    if mag_col_exists:
        tmp = tmp[tmp["mag"] >= 4.0]

    # 3) sort + years
    tmp = tmp.sort_values("__year")
    years = sorted(tmp["__year"].unique().tolist())

    all_features = []
    seen_parts = []

    # helper to get style from mag
    def style_from_mag(mag_val: float):
        # defaults if mag missing
        if mag_val is None:
            return {"color": "#ffcc00", "radius": 4}

        # base radius: start at 4, grow with mag
        # 4.0 -> 4, 5.0 -> 6, 6.0 -> 8, clamp at 10
        base = 4 + (mag_val - 4) * 2
        radius = max(3, min(10, base))

        # color ramp
        if mag_val >= 6.0:
            color = "#d20000"   # strong red
        elif mag_val >= 5.0:
            color = "#ff6600"   # orange
        else:
            color = "#ffcc00"   # yellow

        return {"color": color, "radius": radius}

    for y in years:
        this_year = tmp[tmp["__year"] == y]
        if not this_year.empty:
            seen_parts.append(this_year)

        cum_df = pd.concat(seen_parts, ignore_index=True)

        for _, r in cum_df.iterrows():
            mag_val = float(r["mag"]) if (mag_col_exists and not pd.isna(r["mag"])) else None
            s = style_from_mag(mag_val)

            all_features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [float(r["lon"]), float(r["lat"])],
                },
                "properties": {
                    "time": f"{y:04d}-01-01T00:00:00",
                    "icon": "circle",
                    "iconstyle": {
                        "fillOpacity": 0.75,
                        "stroke": "true",
                        "color": s["color"],     # outline
                        "fillColor": s["color"], # fill
                        "radius": s["radius"],
                    },
                },
            })

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
