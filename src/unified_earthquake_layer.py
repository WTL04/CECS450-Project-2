import folium
from folium.plugins import MarkerCluster
import pandas as pd


def add_unified_earthquake_layer(m, df, mag_min=3.0, sample_limit=2000):
    """
    Add a single unified earthquake layer with multi-dimensional visual encoding:
    - SIZE represents magnitude (dramatically scaled: bigger = stronger)
    - COLOR represents depth (green=shallow, orange=intermediate, purple=deep)

    This allows users to see both magnitude and depth patterns simultaneously.
    """

    # Filter to significant earthquakes
    df_filtered = df[df["mag"] >= mag_min].copy()

    # Sample if needed for performance
    if sample_limit and len(df_filtered) > sample_limit:
        df_filtered = df_filtered.sample(n=sample_limit, random_state=42)

    print(f"Creating unified layer with {len(df_filtered):,} earthquakes (Mag >= {mag_min})")

    # Create marker cluster with optimized settings
    cluster = MarkerCluster(
        name=f"All Earthquakes (Mag >={mag_min}) -- Size=Magnitude, Color=Depth",
        show=False,  # hidden by default - toggle on to explore
        overlay=True,
        control=True,
        options={
            'disableClusteringAtZoom': 9,  # Break apart clusters VERY early (at zoom 9)
            'maxClusterRadius': 40,  # Even smaller cluster radius
            'spiderfyOnMaxZoom': False,  # Don't spiderfy - just show individual markers
            'showCoverageOnHover': False,  # No blue polygon on hover
            'zoomToBoundsOnClick': True
        }
    ).add_to(m)

    for _, r in df_filtered.iterrows():
        mag = r["mag"]
        depth = r["depth"]

        # DRAMATIC magnitude-based sizing (MUCH MUCH bigger - highly visible)
        if mag >= 7.0:
            radius = 35  # Massive - unmissable!
        elif mag >= 6.0:
            radius = 25  # Very large
        elif mag >= 5.0:
            radius = 18  # Large
        elif mag >= 4.0:
            radius = 12  # Medium
        else:
            radius = 8   # Small but still visible

        # Depth-based coloring (adjusted for California's shallow crustal geology)
        # 99.7% of CA quakes are <30km, so we need finer distinctions
        if depth < 10:
            color = "#50c878"  # Green - very shallow (most damaging, surface-level)
            depth_label = "Very Shallow (0-10 km)"
        elif depth < 20:
            color = "#ff8c00"  # Orange - shallow (moderate depth)
            depth_label = "Shallow (10-20 km)"
        else:
            color = "#9b59b6"  # Purple - deeper (relatively deep for CA)
            depth_label = "Deeper (>20 km)"

        # Clean, simple popup
        popup_html = f"""
        <div style='font-family: Arial; font-size: 13px; min-width: 180px;'>
            <div style='border-bottom: 2px solid {color}; margin-bottom: 8px; padding-bottom: 4px;'>
                <b style='font-size: 16px;'>Magnitude {mag:.1f}</b>
            </div>
            <b>Depth:</b> {depth:.1f} km
            <span style='color: {color}; font-weight: bold;'>({depth_label})</span><br>
            <b>Date:</b> {r.datetime.strftime('%Y-%m-%d') if hasattr(r.datetime, 'strftime') else str(r.datetime)[:10]}<br>
            <b>Location:</b> {r.lat:.3f}°, {r.lon:.3f}°
        </div>
        """

        folium.CircleMarker(
            [r.lat, r.lon],
            radius=radius,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.6,
            weight=2,
            opacity=0.8,
            popup=folium.Popup(popup_html, max_width=250)
        ).add_to(cluster)

    return m
