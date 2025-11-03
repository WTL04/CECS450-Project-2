import folium
from folium import FeatureGroup
from folium.plugins import MarkerCluster

def add_magnitude_layers(m, df, sample_limit=800):
    """
    Add magnitude-based earthquake layers with clustering for performance.
    Standardized visual design: blue (small) → yellow (medium) → red (large)
    sample_limit: max markers per magnitude bin (default 800)
    """
    # Standardized color scheme for magnitude
    mag_bins = {
        "M < 3": {"range": (0, 3), "color": "#4a90e2", "radius": 3},
        "3 ≤ M < 5": {"range": (3, 5), "color": "#f5a623", "radius": 4},
        "M ≥ 5": {"range": (5, 10), "color": "#d0021b", "radius": 6}
    }

    for label, config in mag_bins.items():
        low, high = config["range"]
        cluster = MarkerCluster(name=f"Filter: Magnitude {label}", show=False).add_to(m)
        subset = df[(df["mag"] >= low) & (df["mag"] < high)]

        # Sample if needed to avoid embedding too many markers
        if sample_limit and len(subset) > sample_limit:
            subset = subset.sample(n=sample_limit, random_state=42)

        for _, r in subset.iterrows():
            # Standardized popup format
            popup_html = f"""
            <div style='font-family: Arial; font-size: 12px; min-width: 150px;'>
                <b style='color: {config["color"]}; font-size: 14px;'>M {r.mag:.1f}</b><br>
                <b>Depth:</b> {r.depth:.1f} km<br>
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

    print(f"Added magnitude filters (3 bins, {len(df):,} total earthquakes)")