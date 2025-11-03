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


def add_depth_filters(m, df, sample_limit=600):
    """
    Adds depth-based clusters with California-specific visual encoding:
    - Circle color = depth (green/orange/purple)
    - Circle size = magnitude (8–35 px scale)
    """
    _ensure_popup_css(m)
    print(f"[depth] adding layers @ sample_limit={sample_limit} …")

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

    shallow_vs = df[df["depth"] < 10]
    shallow = df[(df["depth"] >= 10) & (df["depth"] < 20)]
    deeper = df[df["depth"] >= 20]

    groups = [
        ("Depth: 0–10 km (Very Shallow)", shallow_vs),
        ("Depth: 10–20 km (Shallow)", shallow),
        ("Depth: >20 km (Deeper)", deeper)
    ]

    for title, subset in groups:
        cluster = MarkerCluster(name=title)
        for _, r in subset.head(sample_limit).iterrows():
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
                fill_opacity=0.55,
                weight=1,
                popup=folium.Popup(html, max_width=280),
            ).add_to(cluster)
        cluster.add_to(m)

    print("[depth] done.")
    return (df["depth"].min(), df["depth"].max())

