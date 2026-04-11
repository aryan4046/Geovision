import { useState, useEffect } from "react";
import { Search, Layers, ZoomIn, ZoomOut, Sparkles, Navigation } from "lucide-react";
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
  restaurant: "🍽️ Restaurant",
  warehouse: "📦 Warehouse",
  "ev-station": "⚡ EV Station",
  retail: "🛍️ Retail Store",
  office: "🏢 Office Space",
  hotel: "🏨 Hotel",
};

type MapViewProps = {
  selectedLocation: LocationData | null;
  onMapClick?: (lat: number, lng: number) => void;
  businessType: string;
  onBusinessTypeChange: (type: string) => void;
  showHeatmap: boolean;
  onToggleHeatmap: (show: boolean) => void;
};

function MapEvents({ onMapClick }: { onMapClick?: (lat: number, lng: number) => void }) {
  useMapEvents({
    click(e) {
      if (onMapClick) onMapClick(e.latlng.lat, e.latlng.lng);
    },
  });
  return null;
}

export function MapView({
  selectedLocation,
  onMapClick,
  businessType,
  onBusinessTypeChange,
  showHeatmap,
  onToggleHeatmap,
}: MapViewProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [hotspots, setHotspots] = useState<any[]>([]);

  useEffect(() => {
    if (showHeatmap) {
      apiService.fetchHotspots().then(data => {
        // detect_hotspots returns { hotspots: [...], total_clusters, noise_points }
        setHotspots(data.hotspots || data.clusters || []);
      }).catch(console.error);
    } else {
      setHotspots([]);
    }
  }, [showHeatmap]);

  const defaultCenter: [number, number] = [20.5937, 78.9629]; // India base

  return (
    <div className="flex-1 relative overflow-hidden bg-slate-100">
      
      {/* Map Container */}
      <div className="absolute inset-0 z-0">
        <MapContainer
          center={selectedLocation ? [selectedLocation.lat, selectedLocation.lng] : defaultCenter}
          zoom={5}
          minZoom={4}
          maxBounds={[
            [6.0, 68.0],  // Southwest India
            [37.5, 97.5]  // Northeast India
          ]}
          maxBoundsViscosity={1.0}
          style={{ height: "100%", width: "100%", background: "#e8edf2" }}
          zoomControl={false}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          <MapEvents onMapClick={onMapClick} />
          
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
        </MapContainer>
      </div>

      {/* Top Controls Overlay */}
      <div className="absolute top-6 left-6 right-6 flex items-center justify-between z-10 pointer-events-none">
        
        {/* Search & Filters */}
        <div className="flex gap-3 pointer-events-auto">
          {/* Search Bar */}
          <div
            className="flex items-center gap-2 px-4 py-3 rounded-xl w-80 shadow-2xl transition-all border border-white/10"
            style={{ background: "rgba(8,12,24,0.85)", backdropFilter: "blur(16px)" }}
          >
            <Search className="w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search city, neighborhood, pin..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="bg-transparent border-none outline-none text-sm text-white w-full placeholder-gray-500"
            />
            {searchQuery && (
              <button onClick={() => setSearchQuery("")} className="text-gray-400 hover:text-white">
                <Search className="w-3.5 h-3.5" />
              </button>
            )}
          </div>

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
          {/* Heatmap Toggle */}
          <button
            onClick={() => onToggleHeatmap(!showHeatmap)}
            className="flex items-center gap-2 px-4 py-3 rounded-xl transition-all border shadow-2xl"
            style={{
              background: showHeatmap
                ? "linear-gradient(135deg, rgba(239,68,68,0.2), rgba(249,115,22,0.2))"
                : "rgba(8,12,24,0.85)",
              border: showHeatmap ? "1px solid rgba(239,68,68,0.4)" : "1px solid rgba(255,255,255,0.1)",
              backdropFilter: "blur(16px)",
            }}
          >
            <Layers
              className="w-4 h-4"
              style={{ color: showHeatmap ? "#f87171" : "rgba(156,163,175,1)" }}
            />
            <span
              className="text-sm font-medium"
              style={{ color: showHeatmap ? "#fca5a5" : "white" }}
            >
              Density Map
            </span>
          </button>

          {/* AI Suggest Location */}
          <button
            className="flex items-center gap-2 px-4 py-3 rounded-xl transition-all shadow-2xl overflow-hidden relative group border border-purple-500/30"
            style={{ background: "rgba(8,12,24,0.85)", backdropFilter: "blur(16px)" }}
            onClick={() => {
              window.location.href = '/recommendations';
            }}
          >
            <div className="absolute inset-0 bg-gradient-to-r from-purple-600/20 to-blue-600/20 opacity-0 group-hover:opacity-100 transition-opacity" />
            <Sparkles className="w-4 h-4 text-purple-400 group-hover:text-purple-300 transition-colors" />
            <span className="text-sm font-medium text-purple-100">Find Best Spots</span>
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
      {!selectedLocation && (
        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 z-10">
           <div className="px-6 py-3 rounded-full border border-purple-500/30 shadow-2xl flex items-center gap-2" style={{ background: "rgba(8,12,24,0.85)", backdropFilter: "blur(16px)" }}>
             <Sparkles className="w-4 h-4 text-purple-400" />
             <p className="text-sm text-gray-200">Select a location on the map to analyze</p>
           </div>
        </div>
      )}
    </div>
  );
}
