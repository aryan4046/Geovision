from fastapi import APIRouter, HTTPException, Query
import urllib.request
import urllib.parse
import json

router = APIRouter()

def photon_to_nominatim(feature):
    props = feature.get("properties", {})
    coords = feature.get("geometry", {}).get("coordinates", [0, 0])
    
    # Coordinates in GeoJSON are [lon, lat]
    lon, lat = coords[0], coords[1]
    
    # Harmonize keys for frontend compatibility
    if "street" in props and "road" not in props:
        props["road"] = props["street"]
    if "district" in props and "suburb" not in props:
        props["suburb"] = props["district"]
    
    # Build a display name like Nominatim
    name = props.get("name", "")
    parts = []
    if name: 
        parts.append(name)
    for key in ["street", "suburb", "city", "county", "state", "country"]:
        val = props.get(key)
        if val and val not in parts:
            parts.append(val)
            
    display_name = ", ".join(parts) if parts else "Unknown Location"
    
    return {
        "lat": str(lat),
        "lon": str(lon),
        "name": name,
        "display_name": display_name,
        "address": props,
    }

@router.get("/geocoder/search")
async def geocode_search(q: str, limit: int = 5, addressdetails: int = 1):
    try:
        # Append India to the query to heavily bias the search towards India
        search_query = q if "india" in q.lower() else f"{q} India"
        url = f"https://photon.komoot.io/api/?q={urllib.parse.quote(search_query)}&limit={max(limit * 3, 15)}"
        
        req = urllib.request.Request(url, headers={'User-Agent': 'GeoVisionAI/1.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            
            features = data.get("features", [])
            
            # Filter results strictly to India
            india_features = []
            for f in features:
                p = f.get("properties", {})
                country_code = p.get("countrycode", "").upper()
                country = p.get("country", "").lower()
                if country_code == "IN" or country == "india":
                    india_features.append(f)
            
            # Map top 'limit' results to nominatim format
            results = [photon_to_nominatim(f) for f in india_features[:limit]]
            return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search Proxy Error: {str(e)}")

@router.get("/geocoder/reverse")
async def reverse_geocode(lat: float, lng: float, zoom: int = 18, addressdetails: int = 1):
    try:
        url = f"https://photon.komoot.io/reverse?lon={lng}&lat={lat}"
        req = urllib.request.Request(url, headers={'User-Agent': 'GeoVisionAI/1.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            
            features = data.get("features", [])
            if features:
                return photon_to_nominatim(features[0])
            
            # Fallback for empty results
            return {
                "lat": str(lat),
                "lon": str(lng),
                "name": f"Location ({lat:.4f}, {lng:.4f})",
                "display_name": f"Location ({lat:.4f}, {lng:.4f})",
                "address": {}
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reverse Geocode Proxy Error: {str(e)}")
