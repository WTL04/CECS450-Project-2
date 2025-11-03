import folium
from folium import FeatureGroup
from folium.plugins import MarkerCluster


def add_depth_layers(m, df, sample_limit=800):
    """
    Add depth-based earthquake layers with clustering for performance.
    Standardized visual design: green (shallow) → orange (intermediate) → purple (deep)
    sample_limit: max markers per depth bin (default 800)
    """
    # Standardized color scheme for depth
    depth_bins = {
        "Shallow (0–30 km)": {"range": (0, 30), "color": "#50c878", "radius": 4},
        "Intermediate (30–100 km)": {"range": (30, 100), "color": "#ff8c00", "radius": 4},
        "Deep (>100 km)": {"range": (100, 700), "color": "#9b59b6", "radius": 4},
    }

    for label, config in depth_bins.items():
        low, high = config["range"]
        cluster = MarkerCluster(name=f"Filter: Depth {label}", show=False).add_to(m)
        subset = df[(df["depth"] >= low) & (df["depth"] < high)]

        # Sample if needed to avoid embedding too many markers
        if sample_limit and len(subset) > sample_limit:
            subset = subset.sample(n=sample_limit, random_state=42)

        for _, r in subset.iterrows():
            # Standardized popup format
            popup_html = f"""
            <div style='font-family: Arial; font-size: 12px; min-width: 150px;'>
                <b style='color: {config["color"]}; font-size: 14px;'>Depth: {r.depth:.1f} km</b><br>
                <b>Category:</b> {label}<br>
                <b>Magnitude:</b> M {r.mag:.1f}<br>
                <b>Date:</b> {r.datetime.strftime('%Y-%m-%d') if hasattr(r.datetime, 'strftime') else str(r.datetime)[:10]}<br>
                <b>Location:</b> {r.lat:.3f}, {r.lon:.3f}
            </div>
            """

            folium.CircleMarker(
                [r.lat, r.lon],
                radius=config["radius"],
                color=config["color"],
                fill=True,
                fill_color=config["color"],
                fill_opacity=0.7,
                weight=1,
                popup=folium.Popup(popup_html, max_width=200),
            ).add_to(cluster)

    print(f"Added depth filters (3 bins, {len(df):,} total earthquakes)")
