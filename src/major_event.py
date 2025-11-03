import folium
from folium import FeatureGroup, Marker, Icon

def create_major_event_layer(df_major):
    """
    Create a Folium layer for major Southern California earthquakes (1800–2024).
    Each event includes a popup with name, year, magnitude, and a brief fact.
    """
    df = df_major.copy()
    # Add brief one-line facts for context (can expand later)
    facts = {
        "Wrightwood": "A powerful quake on the San Andreas Fault damaged California missions including San Juan Capistrano; around 40 deaths reported.",
        "FortTejon": "Ruptured about 360 km of the San Andreas Fault; one of the largest U.S. quakes ever recorded with two deaths.",
        "OwensValley": "Destroyed the town of Lone Pine, killing about 27 people; left a large visible fault scarp still present today.",
        "LagunaSalada": "Cross-border quake along the Laguna Salada Fault extending into Imperial Valley; area sparsely populated with minimal casualties.",
        "SanJacinto": "Quake on the San Jacinto Fault damaged Hemet and San Jacinto; marked continued activity on this major fault.",
        "VolcanoLake": "Occurred near the U.S.–Mexico border; produced ground cracking in the Colorado River Delta region, no deaths reported.",
        "SanJacinto1918": "Another rupture of the San Jacinto Fault; strong shaking across southern California, few casualties.",
        "Lompoc": "Offshore quake west of Lompoc caused strong coastal shaking and minor damage; no deaths.",
        "LagunaSalada1934": "Re-ruptured the Laguna Salada Fault in desert terrain; minimal impact due to low population.",
        "Co.RiverDelta": "Quake in the Colorado River Delta produced ground deformation; limited recorded human impact.",
        "ImperialValley": "Ruptured 60 km of the Imperial Fault, damaging irrigation canals and railways; nine deaths recorded.",
        "Manix": "Mojave Desert quake caused surface ruptures and minor damage; no fatalities reported.",
        "KernCounty": "Severe shaking near Tehachapi killed 12 people and caused widespread structural damage in the southern San Joaquin Valley.",
        "BorregoMountain": "Coyote Creek Fault quake produced a 30-mile-long rupture across the desert with no deaths.",
        "SanFernando": "Collapsed freeway interchanges and hospitals in Los Angeles; 65 deaths and major structural failures.",
        "SuperstitionHills": "Twin shocks near the Salton Sea damaged irrigation infrastructure; no fatalities.",
        "Landers": "Multi-fault rupture felt across the western U.S.; one death and extensive rural damage.",
        "BigBear": "Aftershock following Landers damaged mountain towns but caused no deaths.",
        "Northridge": "Blind thrust quake beneath Los Angeles killed 57, injured over 8,700, and caused about $20 billion in damage.",
        "HectorMine": "Remote Mojave Desert quake on military land; little damage and no casualties.",
        "SanSimeon": "Central coast quake damaged Paso Robles downtown; two fatalities from building collapse.",
        "Baja": "Northern Baja California quake felt across southern California; two deaths reported in Mexico.",
    }

    # Handle Ridgecrest events separately based on magnitude
    def get_ridgecrest_fact(event, magnitude):
        if event == "Ridgecrest":
            if magnitude == 6.4:
                return "Foreshock - Initial shock of the 2019 Ridgecrest sequence caused moderate damage but no deaths."
            elif magnitude == 7.1:
                return "Mainshock - Main event one day later ruptured 20 km of fault with structural damage and fires but no fatalities."
        return None

    # Add fact column
    def get_fact(row):
        event = row['Event']
        magnitude = row['Mag']
        
        # Special handling for Ridgecrest
        ridgecrest_fact = get_ridgecrest_fact(event, magnitude)
        if ridgecrest_fact:
            return ridgecrest_fact
            
        # Use regular facts dictionary for other events
        return facts.get(event, f"A major quake in {event}, magnitude {magnitude:.1f}.")
    
    df["fact"] = df.apply(get_fact, axis=1)

    # Build layer
    fg = FeatureGroup(name="Historical: Major Earthquakes (1800–2024)", show=True)
    for _, r in df.iterrows():
        popup_html = f"""
        <b>{r['Event']}</b><br>
        Year: {r['Year']}<br>
        Magnitude: {r['Mag']}<br>
        {r['fact']}
        """
        Marker(
            location=[r["Lat"], r["Lon"]],
            popup=folium.Popup(popup_html, max_width=250),
            icon=Icon(color="red", icon="info-sign", prefix="glyphicon"),
        ).add_to(fg)

    return fg