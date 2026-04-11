import { useState } from "react";
import { Sidebar, Weights } from "./Sidebar";
import { MapView } from "./MapView";
import { InsightsPanel } from "./InsightsPanel";
import { AIChatbot } from "../chatbot/AIChatbot";
import { useLocationAnalysis } from "../../../hooks/useLocationAnalysis";

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
  const [businessType, setBusinessType] = useState<string>("restaurant");
  const [showHeatmap, setShowHeatmap] = useState(false);
  const [showChatbot, setShowChatbot] = useState(false);
  const [weights, setWeights] = useState<Weights>({
    population: 50,
    accessibility: 50,
    competition: 50,
  });

  const handleMapClick = (lat: number, lng: number) => {
    analyzeLocation(lat, lng, weights, businessType);
  };

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
          onBusinessTypeChange={setBusinessType}
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