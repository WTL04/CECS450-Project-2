import kagglehub
import pandas as pd
import folium
from folium import Map, LayerControl
from branca.element import Element
from src.major_event import create_major_event_layer, create_major_event_norcal_layer
from src.unified_earthquake_layer import add_unified_earthquake_layer
from src.map_pop_heatmap import add_pop_heatmap
from src.map_fault_lines import add_fault_lines
from src.filters_clusters import add_filtered_layers

# Download latest version
path = kagglehub.dataset_download("janus137/six-decades-of-california-earthquakes")

print("Path to dataset files:", path)

# setting up dataframe
df_city_loc = pd.read_csv(path + "/cities_usa_latlon.csv")
df_seismic_norcal = pd.read_csv(
    path + "/data_seismic_NorCal_events_iris_1960_to_2024DEC30_20241230a.csv"
)
df_seismic_socal = pd.read_csv(
    path + "/data_seismic_SoCal_1960_to_2024DEC31_20241231a.csv"
)
df_major_events = pd.read_csv(path + "/major_seismic_events_socal_1800to2024.csv")
df_seismic_norcal_events = pd.read_csv("datasets/major_norcal_events.csv")
df_pop = pd.read_csv("datasets/MCNA_-_Population_Points_with_T_D_Standards.csv")

# MERGE NorCal + SoCal for full California coverage (matches benchmark scope!)
print(f"NorCal earthquakes: {len(df_seismic_norcal):,}")
print(f"SoCal earthquakes: {len(df_seismic_socal):,}")
df_california = pd.concat([df_seismic_norcal, df_seismic_socal], ignore_index=True)
print(f"Total California earthquakes: {len(df_california):,}")

# Add year column for decade analysis
df_california["datetime"] = pd.to_datetime(df_california["datetime"], errors="coerce")
df_california["year"] = df_california["datetime"].dt.year

# Prepare data for filters - add year and standardize columns
df_california["depth"] = pd.to_numeric(df_california["depth"], errors="coerce").fillna(0)
# CRITICAL FIX: Depths are in METERS, convert to KILOMETERS
df_california["depth"] = df_california["depth"] / 1000.0
df_california["mag"] = pd.to_numeric(df_california["mag"], errors="coerce")
df_california = df_california.dropna(subset=["lat", "lon", "mag"])

print(f"Depth range: {df_california['depth'].min():.1f} to {df_california['depth'].max():.1f} km")
print(f"Mean depth: {df_california['depth'].mean():.1f} km")

# main map - centered on California
m = Map(location=[37.0, -119.5], zoom_start=6, tiles="cartodbpositron")

print("\n=== Building California Earthquake Visualization ===")
print(f"Dataset: {len(df_california):,} earthquakes (1960-2024)")

# ========== BASE CONTEXT LAYERS ==========
print("\nBase Context...")
add_fault_lines(m)
add_pop_heatmap(m, df_pop)
add_filtered_layers(m, df_california)

# ========== TEMPORAL ANALYSIS ==========
print("Temporal Analysis...")
fg_major_events = create_major_event_layer(df_major_events)
fg_major_events_norcal = create_major_event_norcal_layer(df_seismic_norcal_events)
fg_major_events.add_child(fg_major_events_norcal)
fg_major_events.add_to(m)

# ========== UNIFIED EARTHQUAKE LAYER ==========
print("Multi-Dimensional Earthquake Layer...")
# Single layer showing BOTH magnitude (size) and depth (color)
add_unified_earthquake_layer(m, df_california, mag_min=3.0, sample_limit=2500)

# ========== LAYER CONTROL ==========
print("\nFinalizing visualization...")

# Simple, clean layer control
LayerControl(collapsed=False).add_to(m)

# Add visual legend for understanding the encoding
legend_html = """
<div style="position: fixed; bottom: 50px; left: 50px; width: 300px; height: auto;
            background-color: white; border: 2px solid grey; z-index: 9999; font-size: 13px;
            padding: 12px; border-radius: 5px; box-shadow: 0 0 15px rgba(0,0,0,0.2);">
    <h4 style="margin-top: 0; margin-bottom: 10px;">Visual Encoding</h4>

    <div style="margin-bottom: 10px;">
        <b>Circle Size = Magnitude</b><br>
        <span style="font-size: 14px;">●</span> M 3-4 (Minor)<br>
        <span style="font-size: 20px;">●</span> M 4-5 (Light)<br>
        <span style="font-size: 28px;">●</span> M 5-6 (Moderate)<br>
        <span style="font-size: 38px;">●</span> M 6-7 (Strong)<br>
        <span style="font-size: 48px;">●</span> M 7+ (Major)
    </div>

    <div style="margin-bottom: 10px;">
        <b>Circle Color = Depth</b><br>
        <span style="color: #50c878; font-size: 20px;">●</span> Very Shallow (0-10 km)<br>
        <span style="color: #ff8c00; font-size: 20px;">●</span> Shallow (10-20 km)<br>
        <span style="color: #9b59b6; font-size: 20px;">●</span> Deeper (>20 km)
    </div>

    <div style="font-size: 11px; color: #666; border-top: 1px solid #ddd; padding-top: 8px;">
        <b>💡 Layer Guide:</b><br>
        • <b>All Earthquakes:</b> Toggle on/off, click for details<br>
        • <b>Major Events:</b> Historic quakes (1800-2024)<br>
        • <b>Context Layers:</b> Faults & population toggleable<br>
        • Zoom in to see individual earthquakes
    </div>
</div>
"""

m.get_root().html.add_child(Element(legend_html))

print("\nSaving maps...")
m.save("outputs/master_map.html")
print("Saved outputs/master_map.html")

# ========== GENERATE TIME SLIDER MAP ==========
print("\nGenerating second map with time slider...")
from src.time_slider import add_time_slider_layer

m_timeline = Map(location=[37.0, -119.5], zoom_start=6, tiles="cartodbpositron")

# Add only fault lines (minimal context)
add_fault_lines(m_timeline)

# Add time slider (main focus)
add_time_slider_layer(m_timeline, df_california, mag_min=5.0)

# Add legend for time slider map
legend_timeline = """
<div style="position: fixed; bottom: 50px; left: 50px; width: 280px; height: auto;
            background-color: white; border: 2px solid grey; z-index: 9999; font-size: 13px;
            padding: 12px; border-radius: 5px; box-shadow: 0 0 15px rgba(0,0,0,0.2);">
    <h4 style="margin-top: 0; margin-bottom: 10px;">Temporal View (1960-2024)</h4>

    <div style="margin-bottom: 10px;">
        <b>Circle Size = Magnitude</b><br>
        <span style="font-size: 12px; color: #999;">(Larger circles = stronger quakes)</span>
    </div>

    <div style="margin-bottom: 10px;">
        <b>Circle Color = Depth</b><br>
        <span style="color: #50c878; font-size: 20px;">●</span> Very Shallow (0-10 km)<br>
        <span style="color: #ff8c00; font-size: 20px;">●</span> Shallow (10-20 km)<br>
        <span style="color: #9b59b6; font-size: 20px;">●</span> Deeper (>20 km)
    </div>

    <div style="font-size: 11px; color: #666; border-top: 1px solid #ddd; padding-top: 8px;">
        <b>💡 Controls:</b><br>
        • Click <b>▶ Play</b> to animate through years<br>
        • Drag slider to scrub timeline<br>
        • Watch patterns evolve over 64 years
    </div>
</div>
"""

m_timeline.get_root().html.add_child(Element(legend_timeline))
m_timeline.save("outputs/time_slider_map.html")
print("Saved outputs/time_slider_map.html")

print(f"\nSuccess! Generated 2 visualizations:")
print(f"   1. master_map.html - Interactive exploration")
print(f"   2. time_slider_map.html - Temporal animation")
print(f"\nBoth cover ALL of California with {len(df_california):,} earthquakes")
