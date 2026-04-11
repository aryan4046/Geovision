"""
load_data.py  — GeoVision AI Database Layer
Provides India-specific geospatial data loading with intelligent fallback.
Uses inverse-distance weighting so ANY click in India gets meaningful values.
"""

import json
import math
import os
import csv
import urllib.request
import urllib.parse

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
    
    # Extract just the city root name (e.g. 'Mumbai - Dharavi' -> 'Mumbai')
    base_city = city_name.split(" - ")[0].strip()
    target_state = city_map.get(base_city, "Total (India)")
    
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
    location in India gets a meaningful (non-zero) density estimate.
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
            
    # Increased search radius to 400km so rural areas can still snap to a regional state
    if closest and min_dist < 400:
        return str(closest.get('area', f'Location ({lat:.3f}, {lng:.3f})'))
    return f"Location ({lat:.3f}, {lng:.3f})"


# ─────────────────────────────────────────────
# Nearby competitors — with generous radius fallback
# ─────────────────────────────────────────────

def get_nearby_competitors(lat: float, lng: float, radius_km: float = 10.0) -> list:
    """
    Return competitors within radius_km.
    If none found at 10 km, extends to 25 km automatically.
    """
    competitors = load_competitors()
    nearby = _filter_by_radius(lat, lng, competitors, radius_km)
    if not nearby:
        nearby = _filter_by_radius(lat, lng, competitors, 25.0)
    return nearby

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


# ─────────────────────────────────────────────
# Nearby POIs — with generous radius fallback
# ─────────────────────────────────────────────

def get_nearby_pois(lat: float, lng: float, radius_km: float = 10.0) -> list:
    """
    Return POIs within radius_km.
    Extends radius if needed, preventing UI blocking/timeouts from live API.
    """
    # 1. Try static JSON first
    static = _filter_by_radius(lat, lng, load_pois(), radius_km)
    if static:
        return static

    # 2. Extend radius to 25km (Fast fallback)
    extended = _filter_by_radius(lat, lng, load_pois(), 25.0)
    if extended:
        return extended
        
    return []


def _fetch_overpass_pois(lat: float, lng: float, radius_m: float = 5000) -> list:
    """Fetch POIs from Overpass API (optional live enrichment)."""
    try:
        query = f"""
        [out:json][timeout:5];
        (
          node["amenity"~"school|hospital|university|bank|metro_station|bus_station|park|mall|restaurant"]
               (around:{int(radius_m)},{lat},{lng});
        );
        out center 20;
        """
        encoded = urllib.parse.quote(query)
        url = f"https://overpass-api.de/api/interpreter?data={encoded}"
        req = urllib.request.Request(url, headers={"User-Agent": "GeoVisionAI/1.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        pois = []
        for el in data.get("elements", []):
            tags = el.get("tags", {})
            pois.append({
                "name": tags.get("name", tags.get("amenity", "POI")),
                "lat":  el.get("lat", el.get("center", {}).get("lat", lat)),
                "lng":  el.get("lon", el.get("center", {}).get("lon", lng)),
                "type": tags.get("amenity", "unknown"),
                "distance_km": haversine(lat, lng,
                    el.get("lat", lat), el.get("lon", lng))
            })
        return pois
    except Exception:
        return []


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
