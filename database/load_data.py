import json
import math
import os

# Base directory for the database files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def _load_json(filename):
    filepath = os.path.join(BASE_DIR, filename)
    if not os.path.exists(filepath):
        return []
    with open(filepath, 'r') as file:
        return json.load(file)

def load_population_data():
    """Load population density data from JSON."""
    return _load_json('population.json')

def load_competitors():
    """Load competitors data from JSON."""
    return _load_json('competitors.json')

def load_pois():
    """Load points of interest data from JSON."""
    return _load_json('pois.json')

def load_locations():
    """Load analyzed locations data from JSON."""
    return _load_json('locations.json')

# Utility Functions
def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance in kilometers between two points 
    on the earth (specified in decimal degrees)
    """
    R = 6371.0 # Earth radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c
    return distance

def get_nearby_competitors(lat, lng, radius_km=5.0):
    """
    Get competitors within a specific radius of the given coordinates.
    """
    competitors = load_competitors()
    nearby = []
    for comp in competitors:
        dist = haversine(lat, lng, comp['lat'], comp['lng'])
        if dist <= radius_km:
            comp_copy = comp.copy()
            comp_copy['distance'] = dist
            nearby.append(comp_copy)
    return nearby

def get_population_density(lat, lng, radius_km=5.0):
    """
    Get the population density for the nearest area within the given radius.
    Returns 0 if no area is within the radius.
    """
    pop_data = load_population_data()
    closest_density = 0
    min_dist = float('inf')
    
    for area in pop_data:
        dist = haversine(lat, lng, area['lat'], area['lng'])
        if dist <= radius_km and dist < min_dist:
            min_dist = dist
            closest_density = area.get('density', 0)
            
    return closest_density

def get_nearby_pois(lat, lng, radius_km=5.0):
    """
    Get points of interest within a specific radius of the given coordinates.
    """
    pois = load_pois()
    nearby = []
    for poi in pois:
        dist = haversine(lat, lng, poi['lat'], poi['lng'])
        if dist <= radius_km:
            poi_copy = poi.copy()
            poi_copy['distance'] = dist
            nearby.append(poi_copy)
    return nearby
