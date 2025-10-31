import folium
import numpy as np
from folium.plugins import MarkerCluster
from branca.element import Element  # built into folium, used for adding HTML + JS

def add_sidepanel_listener(m):
    # sets up the right-side panel and JS that updates when you click any quake
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
    # filters down to stronger quakes so we don't overload the map
    d = df.dropna(subset=["lat","lon","mag"]).copy()
    d = d[d["mag"] >= mag_min].copy()
    if "time" in d.columns:
        d = d.sort_values("time", ascending=False)
    d = d.head(limit)

    grp = MarkerCluster(name=f"Quakes (side panel, Mag ≥{mag_min})").add_to(m)

    for _, r in d.iterrows():
        mag = r.get("mag", "")
        t   = str(r.get("time","")).split("+")[0]
        lat = round(float(r["lat"]), 3)
        lon = round(float(r["lon"]), 3)
        dep = r.get("depth", None)
        dep = "—" if dep is None or np.isnan(dep) else round(float(dep), 1)
        mb  = r.get("mag_bin", "")
        city = r.get("nearest_city", None)
        dist = r.get("nearest_km", None)

        # HTML that shows up inside the info panel
        rows = [
            ("Magnitude", mag),
            ("Magnitude bin", mb),
            ("Date/Time (UTC)", t),
            ("Latitude", lat),
            ("Longitude", lon),
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

        folium.CircleMarker(
            location=[float(r["lat"]), float(r["lon"])],
            radius=4, weight=0.8, fill=True, fill_opacity=0.85
        ).add_to(grp).add_child(popup)

    # links the listener so the panel updatess
    add_sidepanel_listener(m)
    return m

