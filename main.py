import kagglehub
import pandas as pd
from folium import Map, LayerControl
from src.layers_decade_mag import add_decade_heat_layers, add_magbin_markers
from src.single_quake_panel import add_sidepanel_quake_layer




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

# interactive map with the decade & magnitude toggles
m = Map(location=[36.7, -119.4], zoom_start=6, tiles="cartodbpositron")
add_decade_heat_layers(m, df_seismic_socal)
add_magbin_markers(m, df_seismic_socal)
LayerControl(collapsed=False).add_to(m)
m.save("outputs/earthquakes_layers.html")
print("Saved outputs/earthquakes_layers.html")

# side panel info
m = Map(location=[36.7, -119.4], zoom_start=6, tiles="cartodbpositron")
add_sidepanel_quake_layer(m, df_seismic_socal, mag_min=4.0, limit=4000)
LayerControl(collapsed=False).add_to(m)
m.save("outputs/earthquake_sidepanel.html")
print("Saved outputs/earthquake_sidepanel.html")

