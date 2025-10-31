import folium
import numpy as np
import pandas as pd
from folium.plugins import MarkerCluster
from branca.element import Element  # lets us embed HTML + JS

def add_sidepanel_listener(m):
    # sets up the right-side panel + JS that updates when any popup opens
    panel = """
    <style>
      .info-panel{
        position:fixed; top:12px; right:12px; width:320px; max-height:60vh;
        overflow:auto; background:#fff; border:1px solid #aaa; border-radius:8px;
        padding:10px; z-index:9999; box-shadow:0 2px 8px rgba(0,0,0,.15);
        font:12px/1.35 -apple-system,Segoe UI,Roboto,Arial;
      }
    </style>
    <div id="info-panel" class="info-panel"><b>Click an earthquake</b></div>
    <script>
      (function(){
        var map = {{MAP_VAR}};
        map.on('popupopen', function(e){
          var html = e.popup.getContent();
          document.getElementById('info-panel').innerHTML = html;
        });
      })();
    </script>
    """
    html = panel.replace("{{MAP_VAR}}", m.get_name())
    m.get_root().html.add_child(Element(html))
    return m


def add_sidepanel_quake_layer(m, df, mag_min=4.0, limit=4000):
    # filter down dataset a bit
    d = df.dropna(subset=["lat","lon","mag"]).copy()
    d = d[d["mag"] >= mag_min]
    if "time" in d.columns:
        d = d.sort_values("time", ascending=False)
    d = d.head(limit)

    # keep clusters for performance but remove the big blue hull
    grp = MarkerCluster(
        name=f"Quakes (side panel, Mag ≥{mag_min})",
        options={
            "showCoverageOnHover": False,   # disable blue coverage polygon
            "spiderfyOnMaxZoom": True,
            "disableClusteringAtZoom": 9    # uncluster when zoomed in close
        }
    ).add_to(m)

    for _, r in d.iterrows():
        mag = r.get("mag", "")
        # ✅ fix: detect the correct time column and format nicely
        raw_time = (
            r.get("time")
            or r.get("Date")
            or r.get("datetime")
            or r.get("time_utc")
            or ""
        )
        if pd.notna(raw_time) and str(raw_time).strip() != "":
            try:
                from datetime import datetime
                t = datetime.fromisoformat(str(raw_time).split("+")[0]).strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                t = str(raw_time)
        else:
            t = "—"

        lat = float(r["lat"])
        lon = float(r["lon"])

        # convert depth to km if value looks huge
        dep_val = r.get("depth", None)
        if dep_val is None or (isinstance(dep_val, float) and np.isnan(dep_val)):
            dep = "—"
        else:
            dv = float(dep_val)
            if dv > 1000:  # probably meters
                dv = dv / 1000.0
            dep = round(dv, 1)

        mb = r.get("mag_bin", "")
        city = r.get("nearest_city", None)
        dist = r.get("nearest_km", None)

        # build HTML content for the popup / side panel
        rows = [
            ("Magnitude", mag),
            ("Magnitude bin", mb),
            ("Date/Time (UTC)", t),
            ("Latitude", round(lat, 3)),
            ("Longitude", round(lon, 3)),
            ("Depth (km)", dep),
        ]
        if city is not None and dist is not None:
            rows.append(("Nearest city", f"{city} ({dist} km)"))

        html = ["<div style='font:12px/1.35 -apple-system,Segoe UI,Roboto,Arial;'>",
                "<div style='font-weight:600;margin-bottom:6px;'>Earthquake Details</div>",
                "<table style='border-collapse:collapse'>"]
        for k,v in rows:
            html.append(
                f"<tr><td style='padding:2px 8px 2px 0;color:#444;'>{k}</td>"
                f"<td style='padding:2px 0'><b>{v}</b></td></tr>"
            )
        html.append("</table></div>")
        popup = folium.Popup("".join(html), max_width=320)

        # small clean circular marker
        folium.CircleMarker(
            location=[lat, lon],
            radius=3, weight=0.5, fill=True, fill_opacity=0.85
        ).add_to(grp).add_child(popup)

    # add JS listener to sync popup with side panel
    add_sidepanel_listener(m)
    return m

    # wire up the listener so clicking a dot fills the side panel
    add_sidepanel_listener(m)
    return m


