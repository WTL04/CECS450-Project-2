import folium
from folium import FeatureGroup

def add_depth_layers(m, df):
    depth_bins = {
        "Shallow (0–30 km)": (0, 30),
        "Intermediate (30–100 km)": (30, 100),
        "Deep (>100 km)": (100, 700),
    }

    for label, (low, high) in depth_bins.items():
        group = FeatureGroup(name=f"Depth {label}")
        subset = df[(df["depth"] >= low) & (df["depth"] < high)]

        for _, r in subset.iterrows():
            folium.CircleMarker(
                [r.lat, r.lon],
                radius=3,
                color="green" if low < 30 else "orange" if low < 100 else "purple",
                fill=True,
                fill_opacity=0.5,
                popup=f"{label}: {r.depth} km, M {r.mag}",
            ).add_to(group)

        group.add_to(m)

    print("Added depth layers (SoCal)")
