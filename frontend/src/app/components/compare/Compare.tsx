import { useState, useEffect } from "react";
import { Sidebar } from "../dashboard/Sidebar";
import { ArrowLeft, TrendingUp, TrendingDown, Zap } from "lucide-react";
import { Button } from "../ui/button";
import { Progress } from "../ui/progress";
import { useNavigate } from "react-router";
import { apiService } from "../../../services/apiService";

export function Compare() {
  const navigate = useNavigate();
  const [selectedLocations, setSelectedLocations] = useState<any[]>([]);
  const [summary, setSummary] = useState<string>("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Calling with two default locations for comparison demonstration
    apiService.fetchComparison({ lat: 19.076, lng: 72.877 }, { lat: 19.113, lng: 72.869 })
      .then(data => {
        setSelectedLocations(data.comparison || []);
        setSummary(data.recommendation || "");
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="h-screen w-full flex bg-gradient-to-br from-black via-[#0a0a1a] to-[#1a0a2e] overflow-hidden">
      <Sidebar />

      <div className="flex-1 overflow-y-auto">
        <div className="p-8">
          {/* Header */}
          <div className="mb-8">
            <Button
              variant="ghost"
              onClick={() => navigate("/dashboard")}
              className="text-gray-400 hover:text-white mb-4"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Map
            </Button>
            <h1 className="text-3xl font-bold text-white mb-2">Compare Locations</h1>
            <p className="text-gray-400">Side-by-side comparison of top locations</p>
          </div>

          {/* Comparison Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {loading ? (
              <div className="col-span-1 md:col-span-3 flex flex-col items-center justify-center py-20 space-y-4">
                 <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500"></div>
                 <p className="text-gray-400">Loading Comparison...</p>
              </div>
            ) : selectedLocations.length === 0 ? (
              <div className="col-span-1 md:col-span-3 text-center text-gray-400 py-10">No comparisons found.</div>
            ) : selectedLocations.map((location, index) => {
              const getScoreColor = (score: number) => {
                if (score >= 85) return "from-green-500 to-green-600";
                if (score >= 70) return "from-yellow-500 to-yellow-600";
                return "from-red-500 to-red-600";
              };

              return (
                <div
                  key={location.id}
                  className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-6 hover:border-purple-500/50 transition-all"
                >
                  {/* Badge */}
                  {index === 0 && (
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-gradient-to-r from-purple-600 to-blue-600 text-white text-xs font-medium mb-4">
                      ⭐ Recommended
                    </div>
                  )}

                  {/* Location Name */}
                  <h3 className="text-xl font-bold text-white mb-4">{location.name}</h3>

                  {/* Score Display */}
                  <div className="mb-6">
                    <div className="flex items-end gap-2 mb-2">
                      <span className="text-5xl font-bold bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">
                        {location.score}
                      </span>
                      <span className="text-gray-400 mb-2">/100</span>
                    </div>
                    <div className={`h-2 rounded-full bg-gradient-to-r ${getScoreColor(location.score)}`}></div>
                  </div>

                  {/* Metrics */}
                  <div className="space-y-4 mb-6">
                    <div>
                      <div className="flex justify-between mb-2">
                        <span className="text-sm text-gray-300">Population</span>
                        <span className="text-sm font-medium text-white">{location.population}%</span>
                      </div>
                      <Progress value={location.population} className="h-2" />
                    </div>
                    <div>
                      <div className="flex justify-between mb-2">
                        <span className="text-sm text-gray-300">Accessibility</span>
                        <span className="text-sm font-medium text-white">{location.accessibility}%</span>
                      </div>
                      <Progress value={location.accessibility} className="h-2" />
                    </div>
                    <div>
                      <div className="flex justify-between mb-2">
                        <span className="text-sm text-gray-300">Competition</span>
                        <span className="text-sm font-medium text-white">{location.competition}%</span>
                      </div>
                      <Progress value={location.competition} className="h-2" />
                    </div>
                    <div>
                      <div className="flex justify-between mb-2">
                        <span className="text-sm text-gray-300">POIs</span>
                        <span className="text-sm font-medium text-white">{location.pois}%</span>
                      </div>
                      <Progress value={location.pois} className="h-2" />
                    </div>
                  </div>

                  {/* Pros */}
                  <div className="mb-4">
                    <div className="flex items-center gap-2 mb-3">
                      <TrendingUp className="w-4 h-4 text-green-500" />
                      <span className="text-sm font-medium text-white">Pros</span>
                    </div>
                    <ul className="space-y-2">
                      {location.pros?.map((pro: string, idx: number) => (
                        <li key={idx} className="text-sm text-gray-300 flex items-start gap-2">
                          <span className="text-green-500">✓</span>
                          <span>{pro}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Cons */}
                  <div className="mb-6">
                    <div className="flex items-center gap-2 mb-3">
                      <TrendingDown className="w-4 h-4 text-red-500" />
                      <span className="text-sm font-medium text-white">Cons</span>
                    </div>
                    <ul className="space-y-2">
                      {location.cons?.map((con: string, idx: number) => (
                        <li key={idx} className="text-sm text-gray-300 flex items-start gap-2">
                          <span className="text-red-500">✗</span>
                          <span>{con}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Actions */}
                  <div className="space-y-2">
                    <Button
                      onClick={() => navigate("/dashboard")}
                      className="w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white"
                    >
                      View on Map
                    </Button>
                    <Button
                      variant="outline"
                      className="w-full bg-white/5 border-white/10 text-white hover:bg-white/10"
                    >
                      View Details
                    </Button>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Summary */}
          <div className="mt-8 backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-6">
            <div className="flex items-center gap-3 mb-4">
              <Zap className="w-5 h-5 text-yellow-500" />
              <h3 className="text-lg font-bold text-white">AI Recommendation</h3>
            </div>
            <p className="text-gray-300 mb-4">
              {summary || "AI comparison insights will appear here when location data is loaded."}
            </p>
            <div className="flex gap-3">
              <Button className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white">
                Generate Detailed Report
              </Button>
              <Button
                variant="outline"
                className="bg-white/5 border-white/10 text-white hover:bg-white/10"
              >
                View More Locations
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}