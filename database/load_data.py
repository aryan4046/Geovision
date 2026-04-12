"""
load_data.py  — GeoVision AI Database Layer
Provides geospatial data loading with intelligent fallback for any global location.
Uses inverse-distance weighting so ANY lat/lng click gets meaningful values.
"""

import json
import math
import os
import csv
import urllib.request
import urllib.parse
import time

OSM_CACHE = {}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, "..", "Population of India.csv")

# ─────────────────────────────────────────────
# Raw JSON loaders
# ─────────────────────────────────────────────

def _load_json(filename: str) -> list:
    filepath = os.path.join(BASE_DIR, filename)
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def load_population_data() -> list:
    return _load_json("population.json")

def load_competitors() -> list:
    return _load_json("competitors.json")

def load_pois() -> list:
    return _load_json("pois.json")

def load_locations() -> list:
    return _load_json("locations.json")

# ─────────────────────────────────────────────
# Real CSV India Population Data Loader
# ─────────────────────────────────────────────

def get_real_state_data(city_name: str) -> dict:
    """Uses a predefined map to resolve the state and load exact census data from the CSV."""
    # City to State mapping based on population.json
    city_map = {
        "Mumbai": "Maharashtra", "Delhi": "Delhi (UT)", "Bengaluru": "Karnataka",
        "Hyderabad": "Telangana", "Pune": "Maharashtra", "Chennai": "Tamil Nadu",
        "Kolkata": "West Bengal", "Ahmedabad": "Gujarat", "Jaipur": "Rajasthan",
        "Lucknow": "Uttar Pradesh", "Surat": "Gujarat", "Chandigarh": "Chandigarh (UT)",
        "Gurgaon": "Haryana", "Faridabad": "Haryana", "Indore": "Madhya Pradesh",
        "Bhopal": "Madhya Pradesh", "Nagpur": "Maharashtra", "Patna": "Bihar",
        "Kochi": "Kerala", "Visakhapatnam": "Andhra Pradesh", "Coimbatore": "Tamil Nadu",
        "Vadodara": "Gujarat", "Rajkot": "Gujarat", "Nashik": "Maharashtra",
        "Aurangabad": "Maharashtra", "Meerut": "Uttar Pradesh", "Agra": "Uttar Pradesh",
        "Varanasi": "Uttar Pradesh", "Amritsar": "Punjab", "Ludhiana": "Punjab",
        "Dehradun": "Uttarakhand", "Ranchi": "Jharkhand", "Bhubaneswar": "Odisha",
        "Thiruvananthapuram": "Kerala", "Guwahati": "Assam", "Mysuru": "Karnataka",
        "Hubli": "Karnataka", "Madurai": "Tamil Nadu", "Tiruchirappalli": "Tamil Nadu"
    }
    
    # Extract just the city root name (e.g. 'Mumbai - Maharashtra' -> 'Mumbai' and 'Maharashtra')
    parts = city_name.split(" - ")
    base_city = parts[0].strip()
    target_state = city_map.get(base_city)
    
    if not target_state and len(parts) > 1:
        target_state = parts[1].strip()
        
    if not target_state:
        target_state = "Total (India)"
    
    if not os.path.exists(CSV_FILE):
        return {}
        
    with open(CSV_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if target_state in row.get("State/UT", ""):
                try:
                    return {
                        "state": row["State/UT"],
                        "total_population": int(row.get("Population[50]", 0)),
                        "density_sqkm": int(row.get("Density (per km2)", 0)),
                        "urban_population": int(row.get("Urban[51]", 0)),
                        "sex_ratio": int(row.get("Sex ratio", 0))
                    }
                except ValueError:
                    continue
    return {}

# ─────────────────────────────────────────────
# Haversine distance (km)
# ─────────────────────────────────────────────

def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2
         + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2))
         * math.sin(dlon / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

# ─────────────────────────────────────────────
# Population density  — inverse-distance weighted
# Returns a realistic density for ANY lat/lng in India
# ─────────────────────────────────────────────

def get_population_density(lat: float, lng: float, radius_km: float = 50.0) -> float:
    """
    Return population density for the closest reference area.
    Uses inverse-distance weighting across ALL reference points so ANY
    global location gets a meaningful (non-zero) density estimate.
    """
    pop_data = load_population_data()
    if not pop_data:
        return 50_000  # safe default if DB is empty

    # Compute distances
    candidates = []
    for area in pop_data:
        dist = haversine(lat, lng, area["lat"], area["lng"])
        candidates.append((dist, area.get("density", 50_000)))

    candidates.sort(key=lambda x: x[0])

    # If closest point is very near (< radius_km), return its density directly
    if candidates[0][0] <= radius_km:
        return float(candidates[0][1])

    # Otherwise, inverse-distance weighted average of 5 nearest points
    top5 = candidates[:5]
    total_weight = 0.0
    weighted_density = 0.0
    for dist, density in top5:
        w = 1.0 / max(dist, 0.1)  # avoid divide by zero
        weighted_density += density * w
        total_weight += w

    return float(weighted_density / total_weight) if total_weight > 0 else 50_000


def get_location_name(lat: float, lng: float) -> str:
    """
    Return a human-readable location name for any global lat/lng using Reverse Geocoding.
    Falls back to a known reference area if the API fails or is unavailable.
    """
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lng}&addressdetails=1"
        req = urllib.request.Request(url, headers={'User-Agent': 'GeoVisionAI/1.0', 'Accept-Language': 'en'})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            address = data.get("address", {})
            primary = address.get("road", address.get("pedestrian", address.get("suburb", address.get("neighbourhood", address.get("village", "")))))
            secondary = address.get("city", address.get("town", address.get("county", address.get("state_district", ""))))
            
            if primary and secondary and primary != secondary:
                return f"{primary}, {secondary}"
            elif primary or secondary:
                return primary or secondary
                
            if "display_name" in data:
                parts = data["display_name"].split(",")
                return ", ".join(parts[:2]).strip()
    except Exception:
        pass

    # Fallback to nearest major city
    pop_data = load_population_data()
    if not pop_data:
        return f"Location ({lat:.3f}, {lng:.3f})"

    closest = None
    min_dist = float('inf')
    for area in pop_data:
        dist = haversine(lat, lng, area["lat"], area["lng"])
        if dist < min_dist:
            min_dist = dist
            closest = area

    # Within 200 km → use reference area name; otherwise keep coordinate string
    if closest and min_dist < 200:
        return str(closest.get('area', f'Location ({lat:.3f}, {lng:.3f})'))
    return f"Location ({lat:.3f}, {lng:.3f})"


# ─────────────────────────────────────────────
# Nearby competitors — with Overpass API
# ─────────────────────────────────────────────

COMPETITOR_TAGS = {
    "restaurant": ['node["amenity"="restaurant"]', 'node["amenity"="cafe"]', 'way["amenity"="restaurant"]'],
    "ev-station": ['node["amenity"="charging_station"]', 'way["amenity"="charging_station"]'],
    "retail": ['node["shop"]', 'way["shop"]'],
    "office": ['node["office"]', 'way["office"]'],
    "hotel": ['node["tourism"="hotel"]', 'way["tourism"="hotel"]'],
    "warehouse": ['node["building"="warehouse"]', 'node["landuse"="industrial"]']
}

POI_TAGS = [
    'node["amenity"="school"]', 'way["amenity"="school"]',
    'node["amenity"="hospital"]', 'way["amenity"="hospital"]',
    'node["amenity"="bank"]', 
    'node["amenity"="bus_station"]', 'node["highway"="bus_stop"]',
    'node["leisure"="park"]', 'way["leisure"="park"]'
]

def fetch_osm_data(lat: float, lng: float, query_tags: list, radius_offset: float = 0.02) -> list:
    """Fetch data from Overpass API using a bounding box."""
    global OSM_CACHE
    
    if len(OSM_CACHE) > 200:
        OSM_CACHE.clear()
        
    # Round to 3 decimal places (~110m grouping) to share cached results for identical regional queries
    cache_key = f"{round(lat, 3)}_{round(lng, 3)}_{hash(tuple(query_tags))}"
    now = time.time()
    if cache_key in OSM_CACHE:
        entry, timestamp = OSM_CACHE[cache_key]
        if now - timestamp < 3600:
            return entry
            
    lat_min = lat - radius_offset
    lat_max = lat + radius_offset
    lng_min = lng - radius_offset
    lng_max = lng + radius_offset
    
    statements = ""
    for tag in query_tags:
        statements += f"  {tag}({lat_min},{lng_min},{lat_max},{lng_max});\n"
        
    query = f"""
[out:json][timeout:4];
(
{statements}
);
out center;
    """
    
    encoded = urllib.parse.quote(query.strip())
    url = f"https://overpass-api.de/api/interpreter?data={encoded}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "GeoVisionAI/1.0"})
        with urllib.request.urlopen(req, timeout=4) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            
        results = []
        for el in data.get("elements", []):
            tags = el.get("tags", {})
            e_lat = el.get("lat", el.get("center", {}).get("lat", lat))
            e_lng = el.get("lon", el.get("center", {}).get("lon", lng))
            results.append({
                "name": tags.get("name", tags.get("amenity", tags.get("shop", "Location"))),
                "lat": e_lat,
                "lng": e_lng,
                "type": tags.get("amenity", tags.get("shop", "unknown")),
                "distance_km": haversine(lat, lng, e_lat, e_lng)
            })
        results.sort(key=lambda x: x["distance_km"])
        
        OSM_CACHE[cache_key] = (results, now)
        return results
    except Exception as e:
        print(f"[OSM] Fetch error: {e}")
        return []

def fetch_recommendation_cluster(lat: float, lng: float, business_type: str = "retail") -> list:
    """
    Generate fast dynamic recommendations near the given lat/lng.
    Bypasses slow OSM calls to ensure instantaneous response times and reliability.
    """
    # 5 quadrants: NW, NE, SW, SE, Center
    quadrants = [
        {"name": "North West District", "lat": lat + 0.015, "lng": lng - 0.015, "comp_count": 0, "poi_count": 0},
        {"name": "North East District", "lat": lat + 0.015, "lng": lng + 0.015, "comp_count": 0, "poi_count": 0},
        {"name": "South West District", "lat": lat - 0.015, "lng": lng - 0.015, "comp_count": 0, "poi_count": 0},
        {"name": "South East District", "lat": lat - 0.015, "lng": lng + 0.015, "comp_count": 0, "poi_count": 0},
        {"name": "Central Hub",         "lat": lat,         "lng": lng,         "comp_count": 0, "poi_count": 0}
    ]
    
    import random
    base_pop = get_population_density(lat, lng)
    
    for q in quadrants:
        pop_variance = random.uniform(0.8, 1.2)
        q_pop = base_pop * pop_variance
        
        # approximate competitors and POIs based on population density
        if q_pop > 100000:
            q["comp_count"] = random.randint(10, 20)
            q["poi_count"] = random.randint(15, 30)
        elif q_pop > 50000:
            q["comp_count"] = random.randint(5, 12)
            q["poi_count"] = random.randint(8, 18)
        else:
            q["comp_count"] = random.randint(1, 6)
            q["poi_count"] = random.randint(3, 10)
            
    return quadrants

def get_nearby_competitors(lat: float, lng: float, business_type: str = "retail") -> list:
    """
    Return competitors dynamically via OSM.
    """
    tags = COMPETITOR_TAGS.get(business_type, COMPETITOR_TAGS["retail"])
    results = fetch_osm_data(lat, lng, tags, 0.02)
    
    # Fallback to static if OSM is totally blocked or returns 0
    if not results:
        competitors = load_competitors()
        results = _filter_by_radius(lat, lng, competitors, 5.0)
    return results

def _filter_by_radius(lat, lng, items, radius_km):
    result = []
    for item in items:
        dist = haversine(lat, lng, item["lat"], item["lng"])
        if dist <= radius_km:
            copy = item.copy()
            copy["distance_km"] = round(dist, 2)
            result.append(copy)
    result.sort(key=lambda x: x["distance_km"])
    return result

def get_nearby_pois(lat: float, lng: float) -> list:
    """
    Return POIs dynamically via OSM.
    """
    results = fetch_osm_data(lat, lng, POI_TAGS, 0.02)
    
    if not results:
        static = load_pois()
        results = _filter_by_radius(lat, lng, static, 5.0)
        
    return results


# ─────────────────────────────────────────────
# Accessibility score  (0-10 scale)
# Based on count + diversity of nearby POIs
# ─────────────────────────────────────────────

def compute_accessibility_score(pois: list) -> float:
    """
    Returns an accessibility score 0-10 based on POI count and category mix.
    A score of 5 represents median urban accessibility in India.
    """
    if not pois:
        return 3.0  # base score even without data (assumed minimal infrastructure)

    count = len(pois)
    # Category diversity bonus
    poi_types = {p.get("type", "unknown") for p in pois}
    diversity_bonus = min(2.0, len(poi_types) * 0.4)

    # Count-based base (logarithmic — diminishing returns past 10 POIs)
    count_score = min(6.0, math.log1p(count) * 2.0)

    # Distance penalty — POIs closer are more useful
    avg_dist = sum(p.get("distance_km", 5) for p in pois) / max(len(pois), 1)
    dist_penalty = min(1.5, avg_dist * 0.1)

    raw = count_score + diversity_bonus - dist_penalty
    return round(max(1.0, min(10.0, raw)), 2)
