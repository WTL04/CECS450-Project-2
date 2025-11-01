import folium


def add_fault_lines(m):
    # fault line layer
    folium.raster_layers.TileLayer(
        tiles="https://gis.conservation.ca.gov/server/rest/services/CGS/FaultActivityMapCA/MapServer/tile/{z}/{y}/{x}",
        name="CGS Faults (toggle)",
        attr="California Geological Survey",
        overlay=True,
        control=True,
        show=True,  # show fault lines
        max_zoom=14,
        opacity=0.9,
    ).add_to(m)
