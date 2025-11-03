import folium
from folium import FeatureGroup, Marker, Icon


# Socal major events layer
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
    fg = FeatureGroup(name="Historic Major Earthquakes (1800–2024)")
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

# Norcal major events layer
def create_major_event_norcal_layer(df_seismic_norcal_events):
    years_norcal = [
    2005, 1992, 1994, 2024, 1991, 2014, 1991,
    1992, 2005, 2016, 2010, 2022, 1995, 1991,
    1991, 1980, 2021, 2014, 1984, 1994]

    events_norcal = [
        "CapeMendocino-05M",
        "CapeMendocino-92M",
        "MendocinoFault-94",
        "CapeMendocino-24",
        "OffshoreNorCal-91M",
        "Eureka-14",
        "GordaPlate-91",
        "CapeMendocino-92A",
        "CapeMendocino-05A",
        "Ferndale-16",
        "Eureka-10",
        "Ferndale-22",
        "Ferndale-95",
        "OffshoreNorCal-91F",
        "Honeydew-91",
        "Eureka-80",
        "Petrolia-21",
        "SouthNapa-14",
        "Ferndale-84",
        "DoubleSpringFlat-94",
    ]
    facts_norcal = {
        "CapeMendocino-05M": "Magnitude 7.2 temblor rattled the sea floor roughly 100 miles offshore. Although the quake was felt in Humboldt County, no damage occurred on land.",
        "CapeMendocino-92M": "Offshore quake near Cape Mendocino caused strong shaking in Humboldt County. Damage was observed across the regions with 1,108 structures damaged or destroyed, 356 injuries, and $61 million dollars in damages.",
        "MendocinoFault-94": "Largest magnitude earthquake to occur on 1994 on the Mendocino Fault occurred approximately 85 miles (140 km) offshore west of Cape Mendocino; it was widely felt across Northern California and Southern Oregon but caused virtually no damage due to its remote epicenter.",
        "CapeMendocino-24": "The earthquake occurred on the Mendocino Fault. It generated shaking that was felt across a 500-mile span of the West Coast, from California to Oregon. The National Tsunami Warning Center issued a tsunami warning for the coast, which was canceled after about an hour when it was determined no destructive tsunami was generated.",
        "OffshoreNorCal-91M": "A major offshore quake 95 km from Brookings, Oregon",
        "Eureka-14": "A compressional event that occurred within the Gorda plate, close to the Mendocino Triple Junction. The shaking was felt widely, from San Francisco to parts of Oregon. Because the epicenter was far offshore, shaking intensities on the coast were comparatively low, and there were reports of only minor damage.",
        "GordaPlate-91": "A major intraplate event that occurred within the Gorda plate, which is subducting beneath the North American plate along the Cascadia Subduction Zone. The epicenter was located offshore of the Oregon-California border region. Due to its location far out in the ocean, it was felt in coastal communities but resulted in no reported damage onshore. This event is a characteristic example of the large, compressional earthquakes that frequently occur inside the Gorda plate as it is being squeezed and deformed by the surrounding Pacific and North American plates.",
        "CapeMendocino-92A": "After shock offshore quake near Petrolia caused severe damage, notably triggering a major fire that destroyed a shopping center in Scotia.",
        "CapeMendocino-05A":" Offshore Gorda Plate region; it was widely felt but caused no immediate reports of damage or injuries.",
        "Ferndale-16": "Occurred in the Mendocino Fault Zone, approximately 100 miles west of Ferndale. The fault is the transform boundary between the Pacific Plate and the Gorda Plate. Earthquakes in this zone are typically right-lateral strike-slip (horizontal) events, which is why this earthquake did not produce a large tsunami. It was widely felt across Northern California and as far away as the San Francisco Bay Area. Due to its distance offshore, damage was minimal.",
        "Eureka-10": "Occurred 30 miles (48 km) west-southwest of Eureka, California. Because the epicenter was relatively close to shore, it caused moderate but widespread damage in coastal towns, particularly **Eureka** and **Ferndale**. Damage was estimated at over **$40 million**, and involved shattered windows, toppled chimneys, power outages, and structural damage to hundreds of buildings, including the closure of Eureka's Bayshore Mall and parts of Eureka High School. **35 injuries** were reported.",
        "Ferndale-22": "The shaking was particularly intense, with a maximum Mercalli Intensity of **VIII (Severe)** and the city of **Rio Dell** sustaining the most significant damage. Damages across Humboldt County were estimated at approximately $40 million. About 100 people were displaced. Two deaths were reported, which were attributed to medical emergencies (cardiac arrest) that occurred during or immediately following the earthquake, as emergency services were delayed. 17 people were injured. Notably, one of the highest ground accelerations ever recorded in the US occurred in Rio Dell.",
        "Ferndale-95": "It was widely felt across a large area, from the San Francisco Bay Area to southern Oregon, but caused no damage to populated coastal communities.",
        "OffshoreNorCal-91F": "This quake was likely a foreshock of the 8/17/1991 M6.9 event. The quake had a very shallow depth of 2.6 km (1.6 mi) and was not felt.",
        "Honeydew-91": "It occurred onshore near the towns of Petrolia and Honeydew. The event was part of a sequence of four large earthquakes that shook the North Coast in July and August of 1991.",
        "Eureka-80":"Occurred off the coast of Humboldt County. Two people were injured when portions of on overpass of Highway 101 collapsed on the train tracks",
        "Petrolia-21": "It was initially interpreted as a single event, but subsequent analysis revealed it was two shocks occurring 11 seconds apart. The first shock M5.7 was located offshore on the Mendocino transform fault, and the second, larger shock M6.2 was located onshore near Petrolia. The earthquake caused Very Strong shaking (MMI VII) in Humboldt County, resulting in minor damage, but no major structural collapse. Significantly, it was the largest earthquake to date that successfully triggered the ShakeAlert earthquake early warning system, giving some residents up to 10 seconds of warning.",
        "SouthNapa-14": "The largest earthquake to hit the San Francisco Bay Area in 25 years. The damage was concentrated in Napa and Solano counties, with the city of Napa being the most affected. It caused one fatality and injured over 300 people, and resulted in moderate to severe damage to over 2,000 structures, including many historic buildings. Total economic losses were estimated to be between $443 million and $1 billion.",
        "Ferndale-84": "Due to its distant offshore location, the earthquake caused minimal to no reported damage on land.",
        "DoubleSpringFlat-94": "Struck inland in the southern Pine Nut Mountains, was the largest earthquake in Nevada in 28 years. There was no loss of life and only minor property damage, primarily due to the quake's moderate size and occurrence in a sparsely populated area.",
    }

    # Ensure the lists have the same length as the dataframe or pad/truncate as needed
    num_rows = len(df_seismic_norcal_events)
    
    # Extend or truncate lists to match dataframe length
    years_extended = (years_norcal * ((num_rows // len(years_norcal)) + 1))[:num_rows]
    events_extended = (events_norcal * ((num_rows // len(events_norcal)) + 1))[:num_rows]
    
    # Add columns directly to the original dataframe
    df_seismic_norcal_events['curated_year'] = years_extended
    df_seismic_norcal_events['curated_event'] = events_extended
    
    # Add fact column based on curated events
    df_seismic_norcal_events['curated_fact'] = df_seismic_norcal_events['curated_event'].map(
        lambda x: facts_norcal.get(x, f"Major earthquake event: {x}")
    )
    
    print(f"[INFO] Added curated data to {len(df_seismic_norcal_events)} rows")
    print(f"[INFO] Sample curated events: {df_seismic_norcal_events['curated_event'].head(3).tolist()}")

    # Create map layer using curated data
    fg = FeatureGroup(name="Historic Major NorCal Earthquakes")
    for _, r in df_seismic_norcal_events.iterrows():
        popup_html = f"""
        <b>{r['curated_event']}</b><br>
        Year: {r['curated_year']}<br>
        Original Magnitude: {r.get('mag', 'N/A')}<br>
        Location: {r.get('place', 'Northern California')}<br><br>
        {r['curated_fact']}
        """
        
        Marker(
            location=[r["lat"], r["lon"]], 
            popup=folium.Popup(popup_html, max_width=300),
            icon=Icon(color="blue", icon="info-sign", prefix="glyphicon"),
        ).add_to(fg)

    return fg