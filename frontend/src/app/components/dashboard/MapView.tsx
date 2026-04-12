import { useState, useEffect, useRef } from "react";
import { Search, Layers, ZoomIn, ZoomOut, Sparkles, Navigation, X, Loader2 } from "lucide-react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../ui/select";
import { LocationData } from "./Dashboard";
import { MapContainer, TileLayer, Marker, useMapEvents, useMap, Circle } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import markerIcon2x from "leaflet/dist/images/marker-icon-2x.png";
import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";
import { apiService } from "../../../services/apiService";
import { getLatLngFromPlace, getPlaceFromLatLng, getSuggestionsFromPlace } from "../../../services/locationService";

// Fix Leaflet Default Icon issue
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

const customMarkerIcon = L.divIcon({
  className: "custom-div-icon bg-transparent border-none",
  html: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#7c3aed" width="36" height="36" stroke="white" stroke-width="2">
           <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
           <circle cx="12" cy="10" r="3" fill="white"></circle>
         </svg>`,
  iconSize: [36, 36],
  iconAnchor: [18, 36],
  popupAnchor: [0, -36]
});

const businessLabels: Record<string, string> = {
  restaurant: "Restaurant",
  warehouse: "Warehouse",
  "ev-station": "EV Station",
  retail: "Retail Store",
  office: "Office Space",
  hotel: "Hotel",
};

type MapViewProps = {
  selectedLocation: LocationData | null;
  onMapClick?: (lat: number, lng: number, name?: string) => void;
  businessType: string;
  onBusinessTypeChange: (type: string) => void;
  showHeatmap: boolean;
  onToggleHeatmap: (show: boolean) => void;
};

// ─── Map click handler ───────────────────────────────────────────
function MapEvents({ onMapClick, setMapClickLoading }: { onMapClick?: (lat: number, lng: number, name?: string) => void, setMapClickLoading: (val: boolean) => void }) {
  useMapEvents({
    async click(e) {
      if (onMapClick) {
        setMapClickLoading(true);
        try {
          const addressName = await getPlaceFromLatLng(e.latlng.lat, e.latlng.lng);
          onMapClick(e.latlng.lat, e.latlng.lng, addressName);
        } catch (err) {
          onMapClick(e.latlng.lat, e.latlng.lng);
        } finally {
          setMapClickLoading(false);
        }
      }
    },
  });
  return null;
}

// ─── Programmatic pan/zoom controller ───────────────────────────
function MapController({ target }: { target: { lat: number; lng: number; zoom: number } | null }) {
  const map = useMap();
  const prevTarget = useRef<typeof target>(null);

  useEffect(() => {
    if (!target) return;
    // Only fly if target actually changed (avoid loops on re-render)
    if (
      prevTarget.current &&
      prevTarget.current.lat === target.lat &&
      prevTarget.current.lng === target.lng
    ) return;

    prevTarget.current = target;
    map.flyTo([target.lat, target.lng], target.zoom, { animate: true, duration: 1.2 });
  }, [target, map]);

  return null;
}

// ─── Main component ──────────────────────────────────────────────
export function MapView({
  selectedLocation,
  onMapClick,
  businessType,
  onBusinessTypeChange,
  showHeatmap,
  onToggleHeatmap,
}: MapViewProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [searchLoading, setSearchLoading] = useState(false);
  const [searchError, setSearchError] = useState<string | null>(null);
  const [hotspots, setHotspots] = useState<any[]>([]);
  const [mapTarget, setMapTarget] = useState<{ lat: number; lng: number; zoom: number } | null>(null);
  const [mapClickLoading, setMapClickLoading] = useState(false);
  const [topSpots, setTopSpots] = useState<any[]>([]);
  const [findingSpots, setFindingSpots] = useState(false);

  const [suggestions, setSuggestions] = useState<any[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const searchTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Sync map view when a location is selected via MAP CLICK (propagated up from parent)
  useEffect(() => {
    if (selectedLocation) {
      setMapTarget({ lat: selectedLocation.lat, lng: selectedLocation.lng, zoom: 13 });
    }
  }, [selectedLocation]);

  // Debounced search for suggestions
  useEffect(() => {
    if (searchQuery.trim().length >= 3) {
      if (searchTimeoutRef.current) clearTimeout(searchTimeoutRef.current);
      searchTimeoutRef.current = setTimeout(async () => {
        const results = await getSuggestionsFromPlace(searchQuery);
        setSuggestions(results);
        setShowSuggestions(true);
      }, 600);
    } else {
      setSuggestions([]);
      setShowSuggestions(false);
    }
  }, [searchQuery]);

  useEffect(() => {
    if (showHeatmap) {
      apiService.fetchHotspots().then(data => {
        setHotspots(data.hotspots || data.clusters || []);
      }).catch(console.error);
    } else {
      setHotspots([]);
    }
  }, [showHeatmap]);

  // ── Unified handler: search bar calls this, map click calls onMapClick (Dashboard)
  const handleSearch = async () => {
    if (!searchQuery.trim()) return;

    setSearchLoading(true);
    setSearchError(null);

    try {
      const { lat, lng, label } = await getLatLngFromPlace(searchQuery);

      // 1. Pan the map to the found location
      setMapTarget({ lat, lng, zoom: 13 });

      // 2. Trigger the SAME backend workflow as map click
      if (onMapClick) onMapClick(lat, lng, label);
    } catch (err: any) {
      setSearchError(err.message || "Location not found. Please try again.");
    } finally {
      setSearchLoading(false);
    }
  };

  const handleSearchKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") handleSearch();
  };

  const clearSearch = () => {
    setSearchQuery("");
    setSearchError(null);
    setSuggestions([]);
    setShowSuggestions(false);
  };

  // Default center for India region
  const defaultCenter: [number, number] = [20.5937, 78.9629];
  const indiaBounds = L.latLngBounds([6.4626999, 68.1097], [35.513327, 97.3953586]);

  return (
    <div className="flex-1 relative overflow-hidden bg-slate-100">

      {/* Map Container */}
      <div className="absolute inset-0 z-0">
        <MapContainer
          center={defaultCenter}
          zoom={5}
          minZoom={5}
          maxBounds={indiaBounds}
          maxBoundsViscosity={1.0}
          style={{ height: "100%", width: "100%", background: "#e8edf2" }}
          zoomControl={false}
          worldCopyJump={false}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          {/* Listens to map clicks → calls unified handler in Dashboard */}
          <MapEvents onMapClick={onMapClick} setMapClickLoading={setMapClickLoading} />

          {/* Programmatic pan/zoom (search + location sync) */}
          <MapController target={mapTarget} />

          {selectedLocation && (
            <Marker position={[selectedLocation.lat, selectedLocation.lng]} icon={customMarkerIcon} />
          )}

          {showHeatmap && hotspots.map((spot, i) => (
            <Circle
              key={i}
              center={[spot.lat, spot.lng]}
              radius={Math.max(3000, (spot.intensity || 0.5) * 15000)}
              pathOptions={{
                color: (spot.intensity || 0) > 0.7 ? 'red' : (spot.intensity || 0) > 0.4 ? 'orange' : 'green',
                fillOpacity: 0.3,
                stroke: false
              }}
            />
          ))}

          {/* AI Suggested Top Spots Dots */}
          {topSpots.map((spot, i) => (
             <Marker 
                key={`topspot-${i}`} 
                position={[spot.lat, spot.lng]} 
                icon={L.divIcon({
                  className: "custom-div-icon bg-transparent border-none",
                  html: `<div style="background-color: #ec4899; width: 30px; height: 30px; border-radius: 50%; border: 3px solid white; display: flex; align-items: center; justify-content: center; font-weight: bold; color: white; font-size: 14px; box-shadow: 0 4px 10px rgba(0,0,0,0.5);">${i + 1}</div>`,
                  iconSize: [30, 30],
                  iconAnchor: [15, 15]
                })}
             />
          ))}
        </MapContainer>
      </div>

      {/* Top Controls Overlay */}
      <div className="absolute top-6 left-6 right-6 flex items-center justify-between z-10 pointer-events-none">

        {/* Search & Filters */}
        <div className="flex flex-col gap-2 pointer-events-auto">
          {/* Search Bar */}
          <div className="relative">
            <div
              className="flex items-center gap-2 px-4 py-3 rounded-xl w-80 shadow-2xl transition-all border"
              style={{
                background: "rgba(8,12,24,0.85)",
                backdropFilter: "blur(16px)",
                borderColor: searchError ? "rgba(239,68,68,0.5)" : "rgba(255,255,255,0.1)"
              }}
            >
              {searchLoading ? (
                <Loader2 className="w-4 h-4 text-purple-400 animate-spin flex-shrink-0" />
              ) : (
                <Search className="w-4 h-4 text-gray-400 flex-shrink-0" />
              )}
              <input
                type="text"
                placeholder="Search any city, area, country..."
                value={searchQuery}
                onChange={(e) => { setSearchQuery(e.target.value); setSearchError(null); }}
                onKeyDown={handleSearchKeyDown}
                onFocus={() => setShowSuggestions(suggestions.length > 0)}
                onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
                className="bg-transparent border-none outline-none text-sm text-white w-full placeholder-gray-500"
              />
              {searchQuery && !searchLoading && (
                <button onClick={clearSearch} className="text-gray-400 hover:text-white flex-shrink-0">
                  <X className="w-3.5 h-3.5" />
                </button>
              )}
              <button
                onClick={handleSearch}
                disabled={searchLoading || !searchQuery.trim()}
                className="text-xs px-2 py-1 rounded-lg text-purple-300 hover:text-white hover:bg-purple-600/30 transition-all disabled:opacity-40 disabled:cursor-not-allowed flex-shrink-0"
              >
                Go
              </button>
            </div>

            {/* Auto-suggest dropdown */}
            {showSuggestions && suggestions.length > 0 && (
              <div className="absolute top-full left-0 mt-2 w-80 bg-[#080c18] border border-white/10 rounded-xl shadow-2xl overflow-hidden z-20" style={{ backdropFilter: "blur(16px)" }}>
                {suggestions.map((suggestion, i) => (
                  <button
                    key={i}
                    onClick={() => {
                        setSearchQuery(suggestion.label);
                        setShowSuggestions(false);
                        setMapTarget({ lat: suggestion.lat, lng: suggestion.lng, zoom: 13 });
                        if (onMapClick) onMapClick(suggestion.lat, suggestion.lng, suggestion.label);
                    }}
                    className="w-full text-left px-4 py-3 text-sm text-gray-200 hover:bg-purple-600/30 transition-colors border-b border-white/5 last:border-b-0"
                  >
                    <div className="font-medium text-white">{suggestion.label}</div>
                    <div className="text-xs text-gray-400 truncate">{suggestion.display_name}</div>
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Search Error */}
          {searchError && (
            <div
              className="px-3 py-2 rounded-xl text-xs text-red-300 flex items-center gap-2 w-80"
              style={{ background: "rgba(239,68,68,0.15)", border: "1px solid rgba(239,68,68,0.3)", backdropFilter: "blur(16px)" }}
            >
              <span>⚠</span>
              <span>{searchError}</span>
            </div>
          )}

          {/* Business Type Selector */}
          <div
            className="flex items-center shadow-2xl rounded-xl border border-white/10"
            style={{ background: "rgba(8,12,24,0.85)", backdropFilter: "blur(16px)" }}
          >
            <Select value={businessType} onValueChange={onBusinessTypeChange}>
              <SelectTrigger className="w-[180px] h-full border-none bg-transparent hover:bg-white/5 data-[state=open]:bg-white/5 rounded-xl text-white">
                <SelectValue placeholder="Select business" />
              </SelectTrigger>
              <SelectContent
                style={{
                  background: "rgba(8,12,24,0.95)",
                  backdropFilter: "blur(20px)",
                  border: "1px solid rgba(255,255,255,0.1)",
                }}
              >
                {Object.entries(businessLabels).map(([key, label]) => (
                  <SelectItem
                    key={key}
                    value={key}
                    className="text-gray-200 hover:bg-purple-500/20 hover:text-white"
                  >
                    {label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-3 pointer-events-auto">


          {/* AI Suggest Location */}
          <button
            className="flex items-center gap-2 px-4 py-3 rounded-xl transition-all shadow-2xl overflow-hidden relative group border border-purple-500/30"
            style={{ background: "rgba(8,12,24,0.85)", backdropFilter: "blur(16px)" }}
            disabled={findingSpots}
            onClick={async () => {
              const city = prompt("Enter the city to find the best spots:");
              if (!city) return;
              
              setFindingSpots(true);
              setTopSpots([]);
              try {
                  const { lat, lng } = await getLatLngFromPlace(city);
                  setMapTarget({ lat, lng, zoom: 12 });
                  
                  const data = await apiService.fetchRecommendations(lat, lng, businessType);
                  if (data.locations && data.locations.length > 0) {
                      setTopSpots(data.locations);
                  } else {
                      alert("No spots found in this area.");
                  }
              } catch (e: any) {
                  alert(e.message || "Failed to find the best spots.");
              } finally {
                  setFindingSpots(false);
              }
            }}
          >
            <div className="absolute inset-0 bg-gradient-to-r from-purple-600/20 to-blue-600/20 opacity-0 group-hover:opacity-100 transition-opacity" />
            {findingSpots ? (
              <Loader2 className="w-4 h-4 text-purple-400 animate-spin" />
            ) : (
              <Sparkles className="w-4 h-4 text-purple-400 group-hover:text-purple-300 transition-colors" />
            )}
            <span className="text-sm font-medium text-purple-100">{findingSpots ? "Finding..." : "Find Best Spots"}</span>
          </button>
        </div>
      </div>

      {/* Map Controls (Bottom Right) */}
      <div className="absolute bottom-8 right-8 flex flex-col gap-2 z-10">
        <button
          className="w-10 h-10 rounded-xl flex items-center justify-center transition-all hover:scale-105 shadow-xl border border-white/10 group"
          style={{ background: "rgba(8,12,24,0.85)", backdropFilter: "blur(16px)" }}
          onClick={() => {}}
        >
          <Navigation className="w-4 h-4 text-gray-400 group-hover:text-white" />
        </button>
      </div>

      {/* Instructional Toast overlay if no location selected */}
      {!selectedLocation && !mapClickLoading && (
        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 z-10">
          <div className="px-6 py-3 rounded-full border border-purple-500/30 shadow-2xl flex items-center gap-2" style={{ background: "rgba(8,12,24,0.85)", backdropFilter: "blur(16px)" }}>
            <Sparkles className="w-4 h-4 text-purple-400" />
            <p className="text-sm text-gray-200">Search any location or click anywhere on the map</p>
          </div>
        </div>
      )}

      {/* Loading overlay for map click */}
      {mapClickLoading && (
        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 z-10">
          <div className="px-6 py-3 rounded-full border border-purple-500/30 shadow-2xl flex items-center gap-3" style={{ background: "rgba(8,12,24,0.85)", backdropFilter: "blur(16px)" }}>
            <Loader2 className="w-4 h-4 text-purple-400 animate-spin" />
            <p className="text-sm text-gray-200">Fetching address...</p>
          </div>
        </div>
      )}
    </div>
  );
}
