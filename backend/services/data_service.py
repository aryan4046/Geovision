import json
import os
import sys

# Append parent directories to path if module imports fail directly
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

def get_population_density(lat: float, lng: float):
    """
    Load population.json and extract population data
    """
    try:
        from database.load_data import load_population
        return load_population(lat, lng)
    except ModuleNotFoundError:
        # Mock behavior or local reading
        return {"density": "Mock Density Data"}

def get_nearby_competitors(lat: float, lng: float):
    """
    Load competitors.json and extract nearby competitors
    """
    try:
        from database.load_data import load_competitors
        return load_competitors(lat, lng)
    except ModuleNotFoundError:
        return {"competitors": []}

def get_nearby_pois(lat: float, lng: float):
    """
    Load pois.json and extract POIs
    """
    try:
        from database.load_data import load_pois
        return load_pois(lat, lng)
    except ModuleNotFoundError:
        return {"pois": []}
