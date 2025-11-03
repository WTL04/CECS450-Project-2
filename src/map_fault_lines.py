import folium


def add_fault_lines(m):
    # fault line layer - critical context for understanding earthquake patterns
    folium.raster_layers.TileLayer(
        tiles="https://gis.conservation.ca.gov/server/rest/services/CGS/FaultActivityMapCA/MapServer/tile/{z}/{y}/{x}",
        name="Context: Fault Lines (CA Geological Survey)",
        attr="California Geological Survey",
        overlay=True,
        control=True,
        show=True,  # show by default - critical context
        max_zoom=14,
        opacity=0.7,  # slightly more subtle
    ).add_to(m)
