/**
 * locationService.ts — GeoVision AI
 * Geocodes any place name globally using free OSM Nominatim API through the backend proxy.
 * Used by both the search bar and map-click so they share one unified flow.
 */
import { API_ENDPOINTS } from "../config/apiConfig";

const BASE_URL = (import.meta as any).env?.VITE_API_URL || "http://127.0.0.1:8000";

export interface LatLng {
  lat: number;
  lng: number;
  label?: string;
}

export const getLatLngFromPlace = async (place: string): Promise<LatLng> => {
  if (!place.trim()) throw new Error("Please enter a location to search.");

  const url = `${BASE_URL}${API_ENDPOINTS.GEOCODER_SEARCH}?q=${encodeURIComponent(place)}&limit=1&addressdetails=1`;

  const res = await fetch(url);
  if (!res.ok) throw new Error(`Geocoding request failed (${res.status})`);

  const data = await res.json();

  if (!data || data.length === 0) {
    throw new Error(`Location "${place}" not found in India. Try a more specific name.`);
  }

  const result = data[0];
  
  const addr = result.address || {};
  const cityOrTown = addr.city || addr.town || addr.municipality || addr.county || "";
  const sub = addr.suburb || addr.neighbourhood || addr.village || "";
  let label = result.name || place;
  
  if (sub && cityOrTown && sub !== cityOrTown && !label.includes(sub)) {
    label = `${label}, ${sub}, ${cityOrTown}`;
  } else if (sub && cityOrTown && sub !== cityOrTown) {
    label = `${sub}, ${cityOrTown}`;
  } else if (cityOrTown && !label.includes(cityOrTown)) {
    label = `${label}, ${cityOrTown}`;
  } else if (result.display_name) {
    const parts = result.display_name.split(', ');
    label = parts.length >= 2 ? `${parts[0]}, ${parts[1]}` : parts[0];
  }

  return {
    lat: parseFloat(result.lat),
    lng: parseFloat(result.lon),
    label: label,
  };
};

/**
 * Reverse geocode from lat/lng to get a place name
 */
export const getPlaceFromLatLng = async (lat: number, lng: number): Promise<string> => {
  const url = `${BASE_URL}${API_ENDPOINTS.GEOCODER_REVERSE}?lat=${lat}&lng=${lng}&zoom=18&addressdetails=1`;
  
  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error();
    const data = await res.json();
    
    if (data && data.address) {
      const addr = data.address;
      const primary = addr.road || addr.pedestrian || addr.suburb || addr.neighbourhood || addr.village || addr.building || data.name || "";
      const secondary = addr.city || addr.town || addr.county || addr.state_district || "";
      
      if (primary && secondary && primary !== secondary) {
        return `${primary}, ${secondary}`;
      } else if (primary || secondary) {
        return primary || secondary;
      } else if (data.display_name) {
        const parts = data.display_name.split(', ');
        return parts.slice(0, 2).join(', ');
      }
    }
  } catch (err) {
    console.error("Reverse geocoding failed", err);
  }
  
  return `Location (${lat.toFixed(4)}, ${lng.toFixed(4)})`;
};

/**
 * Fetch autocomplete suggestions for place names (restricted to India)
 */
export const getSuggestionsFromPlace = async (place: string): Promise<any[]> => {
  if (!place.trim() || place.length < 3) return [];
  const url = `${BASE_URL}${API_ENDPOINTS.GEOCODER_SEARCH}?q=${encodeURIComponent(place)}&limit=5&addressdetails=1`;
  
  try {
    const res = await fetch(url);
    if (!res.ok) return [];
    
    const data = await res.json();
    return data.map((item: any) => {
      const addr = item.address || {};
      const primary = addr.road || addr.suburb || addr.neighbourhood || item.name || "";
      const secondary = addr.city || addr.town || addr.state || "";
      let formattedLabel = primary && secondary && primary !== secondary ? `${primary}, ${secondary}` : primary || secondary || item.display_name;
      
      return {
        label: formattedLabel,
        display_name: item.display_name,
        lat: parseFloat(item.lat),
        lng: parseFloat(item.lon)
      };
    });
  } catch (err) {
    console.error("Suggestions failed", err);
    return [];
  }
};
