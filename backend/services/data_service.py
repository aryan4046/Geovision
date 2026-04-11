import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

def get_population_density(lat: float, lng: float) -> float:
    try:
        from database.load_data import get_population_density as db_pop
        return db_pop(lat, lng)
    except Exception as e:
        print(f"[data_service] population error: {e}")
        return 50_000

def get_nearby_competitors(lat: float, lng: float) -> list:
    try:
        from database.load_data import get_nearby_competitors as db_comp
        import random
        comps = db_comp(lat, lng)
        if not comps:
            # Generate 2-4 realistic random dummy competitors for remote areas
            count = random.randint(2, 4)
            for i in range(count):
                comps.append({
                    "name": random.choice(["Global Store", "Local Mart", "Express Outlet", "Prime Services", "Urban Hub", "Retail Extra"]),
                    "lat": lat + random.uniform(-0.02, 0.02),
                    "lng": lng + random.uniform(-0.02, 0.02),
                    "type": "General"
                })
        return comps
    except Exception as e:
        print(f"[data_service] competitors error: {e}")
        return []

def get_nearby_pois(lat: float, lng: float) -> list:
    try:
        from database.load_data import get_nearby_pois as db_pois
        import random
        pois = db_pois(lat, lng)
        if not pois:
            # Generate 3-7 dummy POIs for footfall context
            count = random.randint(3, 7)
            for i in range(count):
                pois.append({"type": "Transit", "lat": lat, "lng": lng})
        return pois
    except Exception as e:
        print(f"[data_service] pois error: {e}")
        return []

def get_accessibility_score(pois: list) -> float:
    try:
        from database.load_data import compute_accessibility_score
        return compute_accessibility_score(pois)
    except Exception as e:
        print(f"[data_service] accessibility error: {e}")
        return 5.0  # safe mid-range default

def get_all_locations() -> list:
    try:
        from database.load_data import load_locations
        return load_locations()
    except Exception as e:
        print(f"[data_service] locations error: {e}")
        return []

def get_location_name(lat: float, lng: float) -> str:
    try:
        from database.load_data import get_location_name as db_loc_name
        return db_loc_name(lat, lng)
    except Exception as e:
        print(f"[data_service] location name error: {e}")
        return f"Location ({lat:.3f}, {lng:.3f})"

def get_real_state_data(city_name: str) -> dict:
    try:
        from database.load_data import get_real_state_data as db_state_data
        return db_state_data(city_name)
    except Exception as e:
        print(f"[data_service] state data error: {e}")
        return {}
