"""
California county filters with color-coded regional headers (flat layout)
and restored styled popups.
"""

import folium
from folium.plugins import MarkerCluster
from branca.element import Element

def _ensure_popup_css(m):
    css = """
    <style id="eq-popup-css">
      .eq-pop h4{margin:0 0 6px 0;font-weight:600;color:#1b5e20;letter-spacing:.2px}
      .eq-pop .bar{height:2px;background:#1b5e20;margin:4px 0 8px 0;border-radius:2px}
      .eq-pop .row{margin:2px 0}
      .eq-tag{padding:1px 6px;border-radius:10px;font-size:11px;font-weight:600;white-space:nowrap}
      .eq-tag.shallow-v{background:#d9f0d8;color:#1b5e20;border:1px solid #b7e3b4}
      .eq-tag.shallow{background:#fff3cd;color:#a86403;border:1px solid #ffe69c}
      .eq-tag.deep{background:#e6e9ff;color:#253996;border:1px solid #c8d0ff}
    </style>
    """
    m.get_root().header.add_child(Element(css))

def _depth_bucket(depth_km):
    try: d = float(depth_km)
    except Exception: d = 0.0
    if 0 <= d < 10:   return ("Very Shallow (0–10 km)", "shallow-v")
    if 10 <= d < 20:  return ("Shallow (10–20 km)", "shallow")
    return ("Deeper (> 20 km)", "deep")

def _popup_html(mag, depth_km, dt, lat, lon):
    label, cls = _depth_bucket(depth_km)
    return f"""
    <div class="eq-pop">
      <h4>Magnitude {mag:.1f}</h4>
      <div class="bar"></div>
      <div class="row"><b>Depth:</b> {depth_km:.1f} km
        <span class="eq-tag {cls}">{label}</span>
      </div>
      <div class="row"><b>Date:</b> {dt}</div>
      <div class="row"><b>Location:</b> {lat:.3f}°, {lon:.3f}°</div>
    </div>
    """

def add_region_filters(m, df, sample_limit: int = 400):
    _ensure_popup_css(m)
    print(f"[region] adding county filters with colored headers @ sample_limit={sample_limit} …")

    regions = {
        "Southern California": ["Los Angeles","Orange","San Diego","Riverside","San Bernardino","Ventura","Santa Barbara","Imperial","Kern"],
        "Central California":  ["Fresno","Kings","Madera","Merced","Monterey","San Benito","San Luis Obispo","Santa Cruz","Santa Clara","San Mateo","Alameda","Contra Costa","San Joaquin","Stanislaus","Tulare"],
        "Northern California": ["Napa","Sonoma","Marin","Solano","Yolo","Sacramento","El Dorado","Placer","Nevada","Sutter","Yuba","Butte","Colusa","Glenn","Tehama","Shasta","Lassen","Modoc","Siskiyou","Trinity","Humboldt","Mendocino","Del Norte","Plumas","Sierra","Amador","Calaveras","Tuolumne","Mariposa","Mono","Inyo","Alpine","Lake"],
    }

    bbox = {
        "Los Angeles": (33.7, 35.0, -119.0, -117.4),
        "Orange": (33.3, 33.9, -118.1, -117.4),
        "San Diego": (32.5, 33.5, -117.6, -116.0),
        "Riverside": (33.3, 34.2, -117.5, -114.5),
        "San Bernardino": (33.3, 35.8, -118.2, -114.5),
        "Ventura": (34.0, 34.6, -119.4, -118.6),
        "Santa Barbara": (34.2, 35.0, -120.2, -119.3),
        "Imperial": (32.6, 33.3, -116.2, -114.7),
        "Kern": (34.8, 36.3, -119.9, -117.4),
        "Fresno": (35.9, 37.6, -120.1, -118.3),
        "Kings": (35.8, 36.4, -120.2, -119.3),
        "Madera": (36.7, 37.5, -120.5, -119.2),
        "Merced": (36.8, 37.7, -121.2, -119.5),
        "Monterey": (35.6, 36.9, -122.0, -120.4),
        "San Benito": (36.4, 37.2, -122.0, -120.6),
        "San Luis Obispo": (35.0, 36.0, -121.4, -119.7),
        "Santa Cruz": (36.8, 37.2, -122.2, -121.5),
        "Santa Clara": (36.8, 37.5, -122.2, -121.2),
        "San Mateo": (37.0, 37.7, -123.0, -122.1),
        "Alameda": (37.4, 37.9, -122.4, -121.4),
        "Contra Costa": (37.7, 38.1, -122.5, -121.6),
        "San Joaquin": (37.5, 38.3, -121.6, -120.9),
        "Stanislaus": (37.3, 38.1, -121.3, -120.4),
        "Tulare": (35.7, 36.6, -119.4, -118.3),
        "Napa": (38.3, 38.9, -123.1, -122.1),
        "Sonoma": (38.1, 39.0, -123.5, -122.3),
        "Marin": (37.7, 38.2, -123.1, -122.4),
        "Solano": (38.0, 38.6, -122.5, -121.5),
        "Yolo": (38.3, 38.9, -122.3, -121.3),
        "Sacramento": (38.3, 38.8, -122.0, -121.0),
        "El Dorado": (38.5, 39.1, -121.1, -119.8),
        "Placer": (38.7, 39.5, -121.3, -120.3),
        "Nevada": (39.0, 39.5, -121.3, -120.5),
        "Sutter": (38.8, 39.3, -122.0, -121.5),
        "Yuba": (39.0, 39.5, -122.0, -121.1),
        "Butte": (39.3, 40.1, -122.3, -121.3),
        "Colusa": (38.8, 39.5, -122.5, -121.8),
        "Glenn": (39.3, 40.0, -123.0, -122.0),
        "Tehama": (39.7, 40.5, -123.0, -121.5),
        "Shasta": (40.3, 41.1, -123.5, -121.5),
        "Lassen": (40.2, 41.3, -121.1, -119.9),
        "Modoc": (41.3, 42.0, -121.5, -119.9),
        "Siskiyou": (41.3, 42.0, -123.8, -121.6),
        "Trinity": (40.4, 41.3, -124.2, -122.8),
        "Humboldt": (40.0, 41.3, -124.4, -123.5),
        "Mendocino": (38.8, 40.4, -124.4, -123.2),
        "Del Norte": (41.5, 42.0, -124.5, -123.8),
        "Plumas": (39.6, 40.3, -121.3, -120.4),
        "Sierra": (39.5, 39.8, -121.0, -120.3),
        "Amador": (38.3, 38.7, -121.1, -120.4),
        "Calaveras": (38.0, 38.6, -121.0, -120.2),
        "Tuolumne": (37.7, 38.3, -120.4, -119.6),
        "Mariposa": (37.2, 38.0, -120.1, -119.5),
        "Mono": (37.6, 38.5, -119.4, -118.2),
        "Inyo": (35.5, 37.7, -118.3, -116.6),
        "Alpine": (38.4, 38.8, -120.0, -119.6),
        "Lake": (38.8, 39.2, -123.2, -122.3),
    }

    region_colors = {
        "Southern California": "#ff4d00",
        "Central California":  "#ffa500",
        "Northern California": "#0072B2",
    }

    # Color-coded, uppercase headers (flat)
    for region_name, counties in regions.items():
        color = region_colors[region_name]
        header_html = f"""
        <script>
        const ctrl = document.querySelector('.leaflet-control-layers-overlays');
        if (ctrl) {{
            const header = document.createElement('div');
            header.innerHTML = '<strong style="color:{color};font-size:13px;">{region_name.upper()}</strong>';
            header.style.margin = '6px 0 3px 4px';
            header.style.paddingTop = '5px';
            header.style.borderTop = '1px solid #ccc';
            ctrl.appendChild(header);
        }}
        </script>
        """
        m.get_root().html.add_child(Element(header_html))

        # County layers under this header
        for county in counties:
            if county not in bbox:
                continue
            lat_min, lat_max, lon_min, lon_max = bbox[county]
            subset = df[
                (df["lat"] >= lat_min) & (df["lat"] <= lat_max) &
                (df["lon"] >= lon_min) & (df["lon"] <= lon_max)
            ]
            if subset.empty:
                continue
            if len(subset) > sample_limit:
                subset = subset.sample(sample_limit, random_state=42)

            cluster = MarkerCluster(
                name=f"{county} County",
                options={"disableClusteringAtZoom": 9, "maxClusterRadius": 40},
                show=False,
            )

            for _, r in subset.iterrows():
                mag = float(r.get("mag", 0.0) or 0.0)
                depth_km = float(r.get("depth", 0.0) or 0.0)
                html = _popup_html(mag, depth_km, r.get("datetime",""), r["lat"], r["lon"])
                folium.CircleMarker(
                    [r["lat"], r["lon"]],
                    radius=max(3.0, min(10.0, mag + 1.5)),
                    color=color, fill=True, fill_color=color, fill_opacity=0.55, weight=1,
                    popup=folium.Popup(html, max_width=280),
                ).add_to(cluster)

            cluster.add_to(m)

    print("[region] colored headers + styled popups restored.")