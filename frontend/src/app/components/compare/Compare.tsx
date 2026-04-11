import { useState, useEffect } from "react";
import { Sidebar } from "../dashboard/Sidebar";
import { ArrowLeft, TrendingUp, TrendingDown, Zap, MapPin, RefreshCw } from "lucide-react";
import { Button } from "../ui/button";
import { Progress } from "../ui/progress";
import { useNavigate } from "react-router";
import { apiService } from "../../../services/apiService";
import { useLocationContext } from "../../../context/LocationContext";

// Default pairs used when the user hasn't selected a location yet
const DEFAULT_PAIRS = [
  { lat: 28.6315, lng: 77.2167, label: "Delhi - Connaught Place" },
  { lat: 19.0596, lng: 72.8295, label: "Mumbai - Bandra West" },
];

export function Compare() {
  const navigate = useNavigate();
  const { selectedLocation, businessType } = useLocationContext();

  const [comparison, setComparison] = useState<any[]>([]);
  const [summary, setSummary] = useState<string>("");
  const [loading, setLoading] = useState(true);

  // Build compare pairs: if user picked a location, compare it against a popular city
  const loc1 = selectedLocation
    ? { lat: selectedLocation.lat, lng: selectedLocation.lng }
    : { lat: DEFAULT_PAIRS[0].lat, lng: DEFAULT_PAIRS[0].lng };
  const loc2 = { lat: DEFAULT_PAIRS[1].lat, lng: DEFAULT_PAIRS[1].lng };

  const runComparison = () => {
    setLoading(true);
    apiService.fetchComparison(loc1, loc2)
      .then(data => {
        setComparison(data.comparison || []);
        setSummary(data.recommendation || "");
      })
      .catch(err => {
        console.error("Compare error:", err);
        setSummary("Could not load comparison. Please try again.");
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => { runComparison(); }, [selectedLocation?.lat, selectedLocation?.lng]);

  const getScoreGradient = (score: number) => {
    if (score >= 75) return "from-green-500 to-green-600";
    if (score >= 55) return "from-yellow-500 to-yellow-600";
    return "from-red-500 to-red-600";
  };

  return (
    <div className="h-screen w-full flex bg-gradient-to-br from-black via-[#0a0a1a] to-[#1a0a2e] overflow-hidden">
      <Sidebar />

      <div className="flex-1 overflow-y-auto">
        <div className="p-8">
          {/* Header */}
          <div className="mb-8">
            <Button variant="ghost" onClick={() => navigate("/dashboard")} className="text-gray-400 hover:text-white mb-4">
              <ArrowLeft className="w-4 h-4 mr-2" /> Back to Map
            </Button>
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold text-white mb-2">Compare Locations</h1>
                <p className="text-gray-400">
                  {selectedLocation
                    ? `Comparing your selected location vs Mumbai - Bandra West`
                    : "Comparing Delhi vs Mumbai — click a location on the map to compare it!"}
                </p>
              </div>
              <Button onClick={runComparison} variant="outline" className="bg-white/5 border-white/10 text-white hover:bg-white/10">
                <RefreshCw className="w-4 h-4 mr-2" /> Refresh
              </Button>
            </div>
          </div>

          {/* Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {loading ? (
              <div className="col-span-2 flex flex-col items-center justify-center py-20 space-y-4">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500"></div>
                <p className="text-gray-400">Analyzing and comparing locations...</p>
              </div>
            ) : comparison.length === 0 ? (
              <div className="col-span-2 text-center text-gray-400 py-10">No comparison data.</div>
            ) : comparison.map((loc, index) => (
              <div
                key={loc.id}
                className={`backdrop-blur-xl bg-white/5 border rounded-2xl p-6 hover:border-purple-500/50 transition-all ${
                  index === 0 ? "border-purple-500/40 ring-1 ring-purple-500/20" : "border-white/10"
                }`}
              >
                {index === 0 && (
                  <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-gradient-to-r from-purple-600 to-blue-600 text-white text-xs font-medium mb-4">
                    ⭐ Top Recommendation
                  </div>
                )}

                <h3 className="text-xl font-bold text-white mb-1">{loc.name}</h3>
                <p className="text-xs text-purple-400 mb-4 flex items-center gap-1">
                  <MapPin className="w-3 h-3" /> {loc.lat?.toFixed(4)}, {loc.lng?.toFixed(4)}
                </p>

                {/* Score */}
                <div className="mb-6">
                  <div className="flex items-end gap-2 mb-2">
                    <span className={`text-5xl font-bold bg-gradient-to-r ${getScoreGradient(loc.score)} bg-clip-text text-transparent`}>
                      {loc.score}
                    </span>
                    <span className="text-gray-400 mb-2">/100 · {loc.grade}</span>
                  </div>
                  <div className={`h-2 rounded-full bg-gradient-to-r ${getScoreGradient(loc.score)}`} />
                </div>

                {/* Metrics */}
                <div className="space-y-3 mb-6">
                  {[
                    { label: "Population Density", value: loc.population },
                    { label: "Accessibility",      value: loc.accessibility },
                    { label: "Low Competition",    value: loc.competition },
                    { label: "Footfall Potential", value: loc.pois },
                  ].map(m => (
                    <div key={m.label}>
                      <div className="flex justify-between mb-1">
                        <span className="text-sm text-gray-300">{m.label}</span>
                        <span className="text-sm font-medium text-white">{m.value ?? 0}%</span>
                      </div>
                      <Progress value={m.value ?? 0} className="h-2" />
                    </div>
                  ))}
                </div>

                {/* Strengths */}
                {loc.pros?.length > 0 && (
                  <div className="mb-4">
                    <div className="flex items-center gap-2 mb-2">
                      <TrendingUp className="w-4 h-4 text-green-500" />
                      <span className="text-sm font-medium text-white">Strengths</span>
                    </div>
                    <ul className="space-y-1">
                      {loc.pros.slice(0, 3).map((p: string, i: number) => (
                        <li key={i} className="text-sm text-gray-300 flex items-start gap-2">
                          <span className="text-green-500">✓</span><span>{p}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Weaknesses */}
                {loc.cons?.length > 0 && (
                  <div className="mb-4">
                    <div className="flex items-center gap-2 mb-2">
                      <TrendingDown className="w-4 h-4 text-red-500" />
                      <span className="text-sm font-medium text-white">Weaknesses</span>
                    </div>
                    <ul className="space-y-1">
                      {loc.cons.slice(0, 2).map((c: string, i: number) => (
                        <li key={i} className="text-sm text-gray-300 flex items-start gap-2">
                          <span className="text-red-500">✗</span><span>{c}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                <Button
                  onClick={() => navigate("/dashboard")}
                  className="w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white mt-2"
                >
                  <MapPin className="w-4 h-4 mr-2" /> View on Map
                </Button>
              </div>
            ))}
          </div>

          {/* AI Summary */}
          {summary && (
            <div className="mt-8 backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-6">
              <div className="flex items-center gap-3 mb-4">
                <Zap className="w-5 h-5 text-yellow-500" />
                <h3 className="text-lg font-bold text-white">AI Recommendation</h3>
              </div>
              <p className="text-gray-300">{summary}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}