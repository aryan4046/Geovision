import { useState, useEffect } from "react";
import { Sidebar, Weights } from "./Sidebar";
import { MapView } from "./MapView";
import { InsightsPanel } from "./InsightsPanel";
import { AIChatbot } from "../chatbot/AIChatbot";
import { useLocationAnalysis } from "../../../hooks/useLocationAnalysis";
import { useLocationContext } from "../../../context/LocationContext";

export type LocationData = {
  id: string;
  name: string;
  lat: number;
  lng: number;
  score: number;
  population: number;
  accessibility: number;
  competition: number;
  pois: number;
  strengths: string[];
  weaknesses: string[];
  opportunities: string[];
};

export function Dashboard() {
  const { selectedLocation, loading, analyzeLocation, competitorImpact } = useLocationAnalysis();
  const { setSelectedLocation: setCtxLocation, setBusinessType: setCtxBusinessType, setWeights: setCtxWeights } = useLocationContext();

  const BUSINESS_WEIGHT_PRESETS: Record<string, Weights> = {
    "retail":      { population: 80, accessibility: 40, competition: 70 },
    "restaurant":  { population: 80, accessibility: 40, competition: 70 },
    "office":      { population: 20, accessibility: 60, competition: 20 },
    "warehouse":   { population: 40, accessibility: 60, competition: 80 },
    "ev-station":  { population: 40, accessibility: 80, competition: 30 },
    "hotel":       { population: 30, accessibility: 35, competition: 35 },
  };

  const [businessType, setBusinessType] = useState<string>("restaurant");
  const [showHeatmap, setShowHeatmap] = useState(false);
  const [showChatbot, setShowChatbot] = useState(false);
  const [weights, setWeights] = useState<Weights>(BUSINESS_WEIGHT_PRESETS["restaurant"]);

  const handleMapClick = (lat: number, lng: number, name?: string) => {
    analyzeLocation(lat, lng, weights, businessType, name).then((loc: any) => {
      if (loc) {
        setCtxLocation(loc);
        setCtxBusinessType(businessType);
        setCtxWeights(weights);
      }
    }).catch(() => {});
  };

  // Re-run analysis if businessType or weights change while a location is selected
  useEffect(() => {
    if (selectedLocation) {
      handleMapClick(selectedLocation.lat, selectedLocation.lng, selectedLocation.name);
    }
  }, [businessType, weights]);

  // Also update context whenever selectedLocation changes
  if (selectedLocation && !loading) {
    setCtxLocation(selectedLocation);
  }

  return (
    <div className="h-screen w-full flex overflow-hidden" style={{ background: "linear-gradient(135deg, #04080f 0%, #080c18 50%, #0c0818 100%)" }}>
      {/* Left Sidebar */}
      <Sidebar weights={weights} onWeightChange={setWeights} />

      {/* Main Map Area */}
      <div className="flex-1 flex">
        <MapView
          selectedLocation={selectedLocation}
          onMapClick={handleMapClick}
          businessType={businessType}
          onBusinessTypeChange={(type) => {
            setBusinessType(type);
            if (BUSINESS_WEIGHT_PRESETS[type]) {
              setWeights(BUSINESS_WEIGHT_PRESETS[type]);
            }
          }}
          showHeatmap={showHeatmap}
          onToggleHeatmap={setShowHeatmap}
        />
      </div>

      {/* Right Insights Panel */}
      {loading ? (
        <div className="w-96 h-full flex flex-col items-center justify-center space-y-4" style={{ background: "rgba(8,12,24,0.97)" }}>
           <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500"></div>
           <p className="text-gray-400">Analyzing Location...</p>
        </div>
      ) : selectedLocation && (
        <InsightsPanel
          location={selectedLocation}
          competitorImpact={competitorImpact}
        />
      )}

      {/* AI Chatbot */}
      <AIChatbot
        isOpen={showChatbot}
        onToggle={() => setShowChatbot(!showChatbot)}
        selectedLocation={selectedLocation}
        businessType={businessType}
      />
    </div>
  );
}