"""
Depth-binned clustered layers with styled popups.
"""

import folium
from folium.plugins import MarkerCluster
import pandas as pd
from branca.element import Element

def _ensure_popup_css(m):
    # same CSS as magnitude file (safe to inject again)
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

def _depth_bins(df):
    df = df.copy()
    df["depth"] = pd.to_numeric(df["depth"], errors="coerce")
    return (
        df[(df["depth"] >= 0) & (df["depth"] < 10)],
        df[(df["depth"] >= 10) & (df["depth"] < 20)],
        df[df["depth"] >= 20],
    )

def _add_cluster(m, name, color, rows, sample_limit: int):
    if rows.empty: return
    if len(rows) > sample_limit:
        rows = rows.sample(sample_limit, random_state=42)

    cluster = MarkerCluster(
        name=name,
        options={"disableClusteringAtZoom": 9, "maxClusterRadius": 40},
        show=False,
    )

    for _, r in rows.iterrows():
        mag = float(r.get("mag", 0.0) or 0.0)
        depth = float(r.get("depth", 0.0) or 0.0)
        html = _popup_html(mag, depth, r.get("datetime",""), r["lat"], r["lon"])
        folium.CircleMarker(
            [r["lat"], r["lon"]],
            radius=max(3.0, min(12.0, 1.2*mag + 1.0)),
            color=color, fill=True, fill_color=color, fill_opacity=0.55, weight=1,
            popup=folium.Popup(html, max_width=280),
        ).add_to(cluster)

    cluster.add_to(m)

def add_depth_filters(m, df, sample_limit: int = 600):
    _ensure_popup_css(m)
    print(f"[depth] adding layers @ sample_limit={sample_limit} …")
    shallow_vs, shallow, deeper = _depth_bins(df)
    _add_cluster(m, "Depth: 0–10 km (Very Shallow)", "#50c878", shallow_vs, sample_limit)
    _add_cluster(m, "Depth: 10–20 km (Shallow)", "#ff8c00", shallow, sample_limit)
    _add_cluster(m, "Depth: > 20 km (Deeper)", "#9b59b6", deeper, sample_limit)
    print("[depth] done.")
