import kagglehub
import pandas as pd
from folium import Map, LayerControl
from src.layers_decade_mag import add_decade_heat_layers, add_magbin_markers
from src.single_quake_panel import add_sidepanel_quake_layer
from src.time_slider import add_time_slider_layer
from src.major_event import create_major_event_layer
from src.filters_clusters import add_filtered_layers
from src.map_pop_heatmap import add_pop_heatmap
from src.map_fault_lines import add_fault_lines

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

df_pop = pd.read_csv("datasets/MCNA_-_Population_Points_with_T_D_Standards.csv")

# main map
m = Map(location=[36.7, -119.4], zoom_start=6, tiles="cartodbpositron")

# fault line layer
add_fault_lines(m)
print("Added fault lines")

# heatmap layer
add_pop_heatmap(m, df_pop)

# interactive map with the decade & magnitude toggles
add_decade_heat_layers(m, df_seismic_socal)
add_magbin_markers(m, df_seismic_socal)
print("Added earthquake_layers")

# side panel info
add_sidepanel_quake_layer(m, df_seismic_socal, mag_min=4.0, limit=4000)
print("Added earthquake_sidepanel")

# time slider layer
add_time_slider_layer(m, df_seismic_socal)
print("Added time_slider")

# Major historic events with custom facts
fg_major_events = create_major_event_layer(df_major_events)
fg_major_events.add_to(m)
print("Added major_event_layer")

# filter system for SoCal earthquake visualization
# add_filtered_layers(m, df_seismic_socal)
# print("Added earthquake_socal_county_map")

LayerControl(collapsed=False).add_to(m)
m.save("outputs/master_map.html")
print("Saved outputs/master_map.html")
