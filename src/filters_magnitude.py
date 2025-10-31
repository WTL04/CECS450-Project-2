import folium
from folium import FeatureGroup
from folium.plugins import MarkerCluster

def add_magnitude_layers(m, df):
    mag_bins = {
        "M < 3": (0, 3),
        "3 ≤ M < 5": (3, 5),
        "M ≥ 5": (5, 10)
    }
    for label, (low, high) in mag_bins.items():
        cluster = MarkerCluster(name=f"Magnitude {label}").add_to(m)
        subset = df[(df["mag"] >= low) & (df["mag"] < high)]

        for _, r in subset.iterrows():
            folium.CircleMarker(
                [r.lat, r.lon],
                radius=2 + r.mag,
                color="darkred" if r.mag >= 5 else "orange" if r.mag >= 3 else "blue",
                fill=True,
                fill_opacity=0.6,
                popup=f"M {r.mag}, Depth {r.depth} km, {r.year}",
            ).add_to(cluster)

    print("Added magnitude clusters (SoCal)")