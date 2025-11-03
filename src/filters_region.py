import folium
from folium.plugins import MarkerCluster
from branca.element import Element
import geopandas as gpd

def _fnum(x, default=0.0):
    try:
        return float(str(x).strip())
    except Exception:
        return default

def _depth_color_and_label(depth_km: float):
    d = _fnum(depth_km)
    if d < 10:
        return "#50c878", "Very Shallow (0–10 km)" 
    elif d < 20:
        return "#ff8c00", "Shallow (10–20 km)"      
    return "#9b59b6", "Deeper (>20 km)"            

def _mag_radius(mag):
    m = _fnum(mag)
    if m >= 7.0: return 35
    if m >= 6.0: return 25
    if m >= 5.0: return 18
    if m >= 4.0: return 12
    return 8

def _popup_html(mag, depth, dt, lat, lon, county):
    color, depth_label = _depth_color_and_label(depth)
    return f"""
    <div style="font:13px/1.35 system-ui,-apple-system,Segoe UI,Roboto,Arial">
      <b>Magnitude:</b> {_fnum(mag):.1f}<br/>
      <b>Depth:</b> {_fnum(depth):.1f} km <span style="color:{color}">•</span> <i>{depth_label}</i><br/>
      <b>County:</b> {county}<br/>
      <b>Date:</b> {dt or "—"}<br/>
      <b>Location:</b> {_fnum(lat):.4f}, {_fnum(lon):.4f}
    </div>
    """

#Region County Mapping
REGIONS = {
    "Southern California": [
        "Los Angeles", "Orange", "San Diego", "Riverside", "San Bernardino",
        "Ventura", "Santa Barbara", "Imperial", "Kern"
    ],
    "Central California": [
        "Fresno", "Kings", "Madera", "Merced", "Monterey", "San Benito",
        "San Luis Obispo", "Santa Cruz", "Santa Clara", "San Mateo",
        "Alameda", "Contra Costa", "San Joaquin", "Stanislaus", "Tulare"
    ],
    "Northern California": [
        "Napa", "Sonoma", "Marin", "Solano", "Yolo", "Sacramento", "El Dorado",
        "Placer", "Nevada", "Sutter", "Yuba", "Butte", "Colusa", "Glenn",
        "Tehama", "Shasta", "Lassen", "Modoc", "Siskiyou", "Trinity",
        "Humboldt", "Mendocino", "Del Norte", "Plumas", "Sierra", "Amador",
        "Calaveras", "Tuolumne", "Mariposa", "Mono", "Inyo", "Alpine", "Lake"
    ],
}

def add_region_layers(
    map_obj: folium.Map,
    df,
    lat_col: str = "lat",
    lon_col: str = "lon",
    mag_col: str = "mag",
    depth_col: str = "depth",
    time_col: str = "datetime",
    per_county_sample: int = 400,
):
    print("[Region Layers] Building county-based clusters…")

    # 🔹 Assign counties from GeoJSON if missing
    counties_url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/california-counties.geojson"
    gdf_counties = gpd.read_file(counties_url)

    gdf_counties = gdf_counties[gdf_counties["name"].notna()]

    gdf_quakes = gpd.GeoDataFrame(
        df.copy(),
        geometry=gpd.points_from_xy(df[lon_col], df[lat_col]),
        crs="EPSG:4326",
    )

    gdf_joined = gpd.sjoin(gdf_quakes, gdf_counties, how="left", predicate="within")
    df = df.copy()
    df["county"] = gdf_joined["name"].fillna("Unknown")
    df = df[df["county"] != "Unknown"]

    print(f"[Auto-Assign] {df['county'].nunique()} valid CA counties found.")

    for county_name, sub in df.groupby("county"):
        if not isinstance(county_name, str):
            continue
        sub = sub.sort_values(by=time_col, ascending=False).head(per_county_sample)
        cluster = MarkerCluster(
            name=f"{county_name} County",
            show=False,
            options={"maxClusterRadius": 35, "disableClusteringAtZoom": 8},
        ).add_to(map_obj)

        for _, r in sub.iterrows():
            lat, lon = _fnum(r.get(lat_col)), _fnum(r.get(lon_col))
            if not lat or not lon:
                continue
            mag, depth = _fnum(r.get(mag_col)), _fnum(r.get(depth_col))
            color, _ = _depth_color_and_label(depth)
            popup = _popup_html(mag, depth, r.get(time_col, ""), lat, lon, county_name)

            folium.CircleMarker(
                location=[lat, lon],
                radius=_mag_radius(mag),
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.6,
                weight=1,
                popup=folium.Popup(popup, max_width=300),
            ).add_to(cluster)

    print("[Region Layers Completed county clustering.")

def add_region_dropdown(map_obj: folium.Map):
    css = """
    <style>
      .leaflet-control-layers, .leaflet-control-layers-toggle {
        display: none !important;
      }
    </style>
    """
    map_obj.get_root().html.add_child(Element(css))

    html = """
    <div style="position: fixed; top: 15px; left: 15px; z-index: 9999;
                background: #fff; border: 1px solid #ccc; border-radius: 8px;
                padding: 12px 14px; width: 270px;
                font: 13px/1.4 system-ui,-apple-system,Segoe UI,Roboto,Arial;
                box-shadow: 0 2px 10px rgba(0,0,0,.15);">
      <b>Filter by Region & County</b>
      <div style="margin-top:8px;">
        <label style="display:block;margin-bottom:4px;">Region</label>
        <select id="rgSel" style="width:100%;padding:6px;border:1px solid #bbb;border-radius:4px;"></select>
      </div>
      <div style="margin-top:8px;">
        <label style="display:block;margin-bottom:4px;">County</label>
        <select id="ctySel" style="width:100%;padding:6px;border:1px solid #bbb;border-radius:4px;"></select>
      </div>
      <div style="margin-top:10px;display:flex;gap:6px;">
        <button id="btnShow" style="flex:1;padding:6px;border:1px solid #aaa;border-radius:4px;background:#f6f6f6;cursor:pointer;">Show</button>
        <button id="btnRegion" style="flex:1;padding:6px;border:1px solid #aaa;border-radius:4px;background:#f6f6f6;cursor:pointer;">Show region</button>
        <button id="btnClear" style="flex:1;padding:6px;border:1px solid #aaa;border-radius:4px;background:#f6f6f6;cursor:pointer;">Clear</button>
      </div>
      <small style="color:#666;display:block;margin-top:8px;">No sidebar. This toggles hidden layer checkboxes under the hood.</small>
    </div>

    <script>
    (function(){
      const REGIONS = {
        "Southern California": ["Los Angeles","Orange","San Diego","Riverside","San Bernardino","Ventura","Santa Barbara","Imperial","Kern"],
        "Central California":  ["Fresno","Kings","Madera","Merced","Monterey","San Benito","San Luis Obispo","Santa Cruz","Santa Clara","San Mateo","Alameda","Contra Costa","San Joaquin","Stanislaus","Tulare"],
        "Northern California": ["Napa","Sonoma","Marin","Solano","Yolo","Sacramento","El Dorado","Placer","Nevada","Sutter","Yuba","Butte","Colusa","Glenn","Tehama","Shasta","Lassen","Modoc","Siskiyou","Trinity","Humboldt","Mendocino","Del Norte","Plumas","Sierra","Amador","Calaveras","Tuolumne","Mariposa","Mono","Inyo","Alpine","Lake"]
      };

      const rgSel = document.getElementById('rgSel');
      const ctySel = document.getElementById('ctySel');
      const btnShow = document.getElementById('btnShow');
      const btnReg = document.getElementById('btnRegion');
      const btnClear = document.getElementById('btnClear');

      Object.keys(REGIONS).forEach(r => {
        const opt = document.createElement('option');
        opt.value = r;
        opt.textContent = r;
        rgSel.appendChild(opt);
      });
      rgSel.value = "Southern California";

      function fillCounties(){
        ctySel.innerHTML = "";
        const list = REGIONS[rgSel.value] || [];
        list.forEach(name => {
          const opt = document.createElement('option');
          opt.value = name + " County";
          opt.textContent = name + " County";
          ctySel.appendChild(opt);
        });
        ctySel.value = list.length ? list[0] + " County" : "";
      }

      rgSel.addEventListener('change', fillCounties);
      fillCounties();

      function layerCheckboxes(){
        const box = document.querySelector('.leaflet-control-layers-overlays');
        if (!box) return [];
        return Array.from(box.querySelectorAll('label')).map(lab => {
          const input = lab.querySelector('input.leaflet-control-layers-selector');
          const text  = lab.textContent.trim();
          return {label:text, input};
        });
      }

      function setLayerChecked(labelText, wanted){
        const items = layerCheckboxes();
        const item = items.find(it => it.label === labelText);
        if (item && item.input && item.input.checked !== wanted) item.input.click();
      }

      function clearAll(){
        layerCheckboxes().forEach(it => {
          if (it.label.endsWith(" County") && it.input.checked) it.input.click();
        });
      }

      function showOnly(labelText){
        const items = layerCheckboxes();
        items.forEach(it => {
          if (it.input.checked && it.label !== labelText) it.input.click();
        });
        setLayerChecked(labelText, true);
      }

      function showRegion(regionName){
        const want = new Set((REGIONS[regionName] || []).map(n => n + " County"));
        const items = layerCheckboxes();

        // Hide everything not in this region
        items.forEach(it => {
          if (it.input.checked && !want.has(it.label)) it.input.click();
        });

        // Only show exact counties from this region
        items.forEach(it => {
          if (want.has(it.label) && !it.input.checked) it.input.click();
        });
      }

      btnShow.addEventListener('click', () => showOnly(ctySel.value));
      btnReg.addEventListener('click', () => showRegion(rgSel.value));
      btnClear.addEventListener('click', clearAll);
    })();
    </script>
    """
    map_obj.get_root().html.add_child(Element(html))
