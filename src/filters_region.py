import folium
from folium import FeatureGroup

def add_region_layers(m, df):
    counties = {
        "Los Angeles County": (33.6, -119.0, 34.8, -117.4),
        "Orange County": (33.4, -118.1, 33.9, -117.4),
        "San Diego County": (32.5, -117.6, 33.6, -116.1),
        "Riverside County": (33.3, -117.6, 34.1, -114.5),
        "San Bernardino County": (33.4, -118.1, 35.0, -114.0),
        "Ventura County": (34.0, -119.4, 34.5, -118.5),
        "Imperial County": (32.6, -116.3, 33.4, -114.7),
        "Santa Barbara County": (34.2, -120.2, 34.8, -118.5)
    }

    for name, (lat_min, lon_min, lat_max, lon_max) in counties.items():
        group = FeatureGroup(name=name)
        subset = df[
            (df["lat"] >= lat_min)
            & (df["lat"] <= lat_max)
            & (df["lon"] >= lon_min)
            & (df["lon"] <= lon_max)
        ]

        for _, r in subset.iterrows():
            folium.CircleMarker(
                [r.lat, r.lon],
                radius=2,
                color="darkred",
                fill=True,
                fill_opacity=0.5,
                popup=f"{name}: M {r.mag}, Depth {r.depth} km",
            ).add_to(group)

        group.add_to(m)

    print(f"Added {len(counties)} county-level layers for SoCal")
