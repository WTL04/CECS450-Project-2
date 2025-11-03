import kagglehub
import pandas as pd
from folium import Map, LayerControl
from branca.element import Element
from src.major_event import create_major_event_layer, create_major_event_norcal_layer
from src.unified_earthquake_layer import add_unified_earthquake_layer
from src.map_pop_heatmap import add_pop_heatmap
from src.map_fault_lines import add_fault_lines
from src.filters_clusters import add_filtered_layers
from src.filters_region import add_region_layers, add_region_dropdown

# ===================================================================
#                      LOAD & PREPARE DATA
# ===================================================================

print("\n=== Loading California Earthquake Dataset ===")
path = kagglehub.dataset_download("janus137/six-decades-of-california-earthquakes")
print(f"Path to dataset files: {path}")

# Read CSVs
df_city_loc = pd.read_csv(path + "/cities_usa_latlon.csv")
df_seismic_norcal = pd.read_csv(path + "/data_seismic_NorCal_events_iris_1960_to_2024DEC30_20241230a.csv")
df_seismic_socal = pd.read_csv(path + "/data_seismic_SoCal_1960_to_2024DEC31_20241231a.csv")
df_major_events = pd.read_csv(path + "/major_seismic_events_socal_1800to2024.csv")
df_seismic_norcal_events = pd.read_csv("datasets/major_norcal_events.csv")
df_pop = pd.read_csv("datasets/MCNA_-_Population_Points_with_T_D_Standards.csv")

# Merge NorCal + SoCal
print(f"\nNorCal earthquakes: {len(df_seismic_norcal):,}")
print(f"SoCal earthquakes: {len(df_seismic_socal):,}")
df_california = pd.concat([df_seismic_norcal, df_seismic_socal], ignore_index=True)
print(f"Total California earthquakes combined: {len(df_california):,}")

# Clean up data
df_california["datetime"] = pd.to_datetime(df_california["datetime"], errors="coerce")
df_california["year"] = df_california["datetime"].dt.year
df_california["depth"] = pd.to_numeric(df_california["depth"], errors="coerce").fillna(0) / 1000.0  # convert m→km
df_california["mag"] = pd.to_numeric(df_california["mag"], errors="coerce")
df_california = df_california.dropna(subset=["lat", "lon", "mag"])

print(f"Depth range: {df_california['depth'].min():.1f}–{df_california['depth'].max():.1f} km")
print(f"Mean depth: {df_california['depth'].mean():.1f} km")

# ===================================================================
#                      MASTER MAP (MAIN VIEW)
# ===================================================================

print("\n=== Building Master Earthquake Map ===")
m = Map(location=[37.0, -119.5], zoom_start=6, tiles="cartodbpositron")

# --- Context Layers ---
print("Adding base context layers...")
add_fault_lines(m)
add_pop_heatmap(m, df_pop)
add_filtered_layers(m, df_california)

# --- Major Historical Events ---
print("Adding major earthquake events...")
fg_major_events = create_major_event_layer(df_major_events)
fg_major_events_norcal = create_major_event_norcal_layer(df_seismic_norcal_events)
fg_major_events.add_child(fg_major_events_norcal)
fg_major_events.add_to(m)

# --- Unified Earthquake Visualization ---
print("Adding unified magnitude/depth layer...")
add_unified_earthquake_layer(m, df_california, mag_min=3.0, sample_limit=2500)

# --- Legend & Layer Control ---
LayerControl(collapsed=False).add_to(m)
legend_html = """
<div style="position: fixed; bottom: 50px; left: 50px; width: 300px;
            background: white; border: 2px solid grey; z-index: 9999;
            font-size: 13px; padding: 12px; border-radius: 6px;
            box-shadow: 0 0 15px rgba(0,0,0,0.2);">
  <h4 style="margin-top: 0;">Visual Encoding</h4>
  <b>Circle Size = Magnitude</b><br>
  <span style="font-size:14px;">●</span> M3–4 (Minor)<br>
  <span style="font-size:20px;">●</span> M4–5 (Light)<br>
  <span style="font-size:28px;">●</span> M5–6 (Moderate)<br>
  <span style="font-size:38px;">●</span> M6–7 (Strong)<br>
  <span style="font-size:48px;">●</span> M7+ (Major)<br><br>
  <b>Circle Color = Depth</b><br>
  <span style="color:#50c878;font-size:20px;">●</span> Very Shallow (0–10 km)<br>
  <span style="color:#ff8c00;font-size:20px;">●</span> Shallow (10–20 km)<br>
  <span style="color:#9b59b6;font-size:20px;">●</span> Deeper (>20 km)<br>
  <hr style="margin:8px 0;">
  <b>💡 Layer Guide:</b><br>
  • Toggle earthquakes & events<br>
  • Enable faults or population density<br>
  • Zoom in for more detail
</div>
"""
m.get_root().html.add_child(Element(legend_html))

# Save master map
m.save("outputs/master_map.html")
print("Saved: outputs/master_map.html")

# ===================================================================
#                      TIME SLIDER MAP
# ===================================================================

print("\n=== Building Time-Slider Earthquake Map ===")
from src.time_slider import add_time_slider_layer

m_timeline = Map(location=[37.0, -119.5], zoom_start=6, tiles="cartodbpositron")

add_fault_lines(m_timeline)
add_time_slider_layer(m_timeline, df_california, mag_min=5.0)

legend_timeline = """
<div style="position: fixed; bottom: 50px; left: 50px; width: 280px;
            background: white; border: 2px solid grey; z-index: 9999;
            font-size: 13px; padding: 12px; border-radius: 6px;
            box-shadow: 0 0 15px rgba(0,0,0,0.2);">
  <h4 style="margin-top: 0;">Temporal View (1960–2024)</h4>
  <b>Circle Size = Magnitude</b><br>
  <span style="font-size:12px;color:#999;">(Larger = stronger quakes)</span><br><br>
  <b>Circle Color = Depth</b><br>
  <span style="color:#50c878;font-size:20px;">●</span> 0–10 km<br>
  <span style="color:#ff8c00;font-size:20px;">●</span> 10–20 km<br>
  <span style="color:#9b59b6;font-size:20px;">●</span> >20 km<br>
  <hr style="margin:8px 0;">
  <b>💡 Controls:</b><br>
  • ▶ Play to animate by year<br>
  • Drag to scrub timeline<br>
  • Observe 64 years of patterns
</div>
"""
m_timeline.get_root().html.add_child(Element(legend_timeline))
m_timeline.save("outputs/time_slider_map.html")
print("Saved: outputs/time_slider_map.html")

# ===================================================================
#                      REGION / COUNTY MAP
# ===================================================================

print("\n=== Building Region / County Filter Map ===")
map_region = Map(location=[37.0, -119.5], zoom_start=6, tiles="cartodbpositron")

add_fault_lines(map_region)
add_region_layers(map_region, df_california)
add_region_dropdown(map_region)

legend_region = """
<div style="position: fixed; bottom: 30px; left: 30px; z-index: 9999;
            background: #fff; padding: 14px 16px; border-radius: 6px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.15);
            font: 13px/1.45 system-ui, -apple-system, 'Segoe UI', Roboto, Arial;
            width: 270px;">
  <b>Region View (1960–2024)</b><br>
  <b>Circle Size = Magnitude</b><br>
  <span style="color:#666;">(Larger = stronger quakes)</span><br><br>
  <b>Circle Color = Depth</b><br>
  <div style="margin-top:4px;">
    <span style="display:inline-block;width:12px;height:12px;background:#50c878;border-radius:50%;margin-right:6px;"></span>
    0–10 km (Very Shallow)
  </div>
  <div style="margin-top:4px;">
    <span style="display:inline-block;width:12px;height:12px;background:#ff8c00;border-radius:50%;margin-right:6px;"></span>
    10–20 km (Shallow)
  </div>
  <div style="margin-top:4px;">
    <span style="display:inline-block;width:12px;height:12px;background:#9b59b6;border-radius:50%;margin-right:6px;"></span>
    >20 km (Deeper)
  </div>
  <hr style="margin:10px 0;border:none;border-top:1px solid #ddd;">
  <b>💡 Controls:</b><br>
  • Filter by region or county<br>
  • Click “Clear” to reset<br>
  • Explore magnitude & depth interactively
</div>
"""
LayerControl(collapsed=False).add_to(map_region)
map_region.get_root().html.add_child(Element(legend_region))
map_region.save("outputs/region_filter_map.html")
print("Saved: outputs/region_filter_map.html")

# ===================================================================
#                      SUMMARY
# ===================================================================

print("\n=== All Maps Generated Successfully ===")
print(f"1. Master Map:      outputs/master_map.html")
print(f"2. Time-Slider Map: outputs/time_slider_map.html")
print(f"3. Region Map:      outputs/region_filter_map.html")
print(f"\nTotal earthquakes visualized: {len(df_california):,}")
print("All three maps are interactive and ready for exploration.\n")
