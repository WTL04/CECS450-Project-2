import folium
from folium.plugins import MarkerCluster
from branca.element import Element


def _popup_html(mag, depth_km, dt, lat, lon):
    # Depth-based coloring (matches unified layer)
    if depth_km < 10:
        color = "#50c878"
        depth_label = "Very Shallow (0-10 km)"
    elif depth_km < 20:
        color = "#ff8c00"
        depth_label = "Shallow (10-20 km)"
    else:
        color = "#9b59b6"
        depth_label = "Deeper (>20 km)"

    return f"""
    <div style='font-family: Arial; font-size: 13px; min-width: 180px;'>
        <div style='border-bottom: 2px solid {color}; margin-bottom: 8px; padding-bottom: 4px;'>
            <b style='font-size: 16px;'>Magnitude {mag:.1f}</b>
        </div>
        <b>Depth:</b> {depth_km:.1f} km
        <span style='color: {color}; font-weight: bold;'>({depth_label})</span><br>
        <b>Date:</b> {dt if dt else 'Unknown'}<br>
        <b>Location:</b> {lat:.3f}°, {lon:.3f}°
    </div>
    """

def add_magnitude_filters(m, df, sample_limit=600):
    print(f"[magnitude] adding layers @ sample_limit={sample_limit} …")

    def _depth_color_and_label(depth):
        if depth < 10:
            return "#50c878", "Very Shallow (0–10 km)"
        elif depth < 20:
            return "#ff8c00", "Shallow (10–20 km)"
        else:
            return "#9b59b6", "Deeper (>20 km)"

    def _mag_radius(mag):
        if mag >= 7.0: return 35
        elif mag >= 6.0: return 25
        elif mag >= 5.0: return 18
        elif mag >= 4.0: return 12
        else: return 8

    minor = df[df["mag"] < 3.0]
    mid = df[(df["mag"] >= 3.0) & (df["mag"] < 5.0)]
    major = df[df["mag"] >= 5.0]

    groups = [
        ("Magnitude < 3.0 (Minor)", minor),
        ("Magnitude 3.0–5.0 (Light–Moderate)", mid),
        ("Magnitude ≥ 5.0 (Strong+)", major)
    ]

    for title, subset in groups:
        cluster = MarkerCluster(
            name=title,
            options={
                'disableClusteringAtZoom': 9,  # Match unified layer
                'maxClusterRadius': 40,
                'spiderfyOnMaxZoom': False,
                'showCoverageOnHover': False,
                'zoomToBoundsOnClick': True
            }
        )
        # Sample from entire dataset, not just head (which may be geographically biased)
        sampled = subset.sample(n=min(sample_limit, len(subset)), random_state=42) if len(subset) > sample_limit else subset
        for _, r in sampled.iterrows():
            mag = float(r.get("mag", 0.0) or 0.0)
            depth = float(r.get("depth", 0.0) or 0.0)
            html = _popup_html(mag, depth, r.get("datetime", ""), r["lat"], r["lon"])

            color, _ = _depth_color_and_label(depth)
            folium.CircleMarker(
                [r["lat"], r["lon"]],
                radius=_mag_radius(mag),
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.6,
                weight=2,
                opacity=0.8,
                popup=folium.Popup(html, max_width=250),
            ).add_to(cluster)
        cluster.add_to(m)

    print("[magnitude] done.")
    return (df["mag"].min(), df["mag"].max())
