import { useState, useEffect } from "react";
import { Sidebar } from "../dashboard/Sidebar";
import { ArrowLeft, MapPin, TrendingUp, Sparkles, ExternalLink } from "lucide-react";
import { Button } from "../ui/button";
import { useNavigate } from "react-router";
import { apiService } from "../../../services/apiService";

export function Recommendations() {
  const navigate = useNavigate();
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiService.fetchRecommendations()
      .then(data => {
        setRecommendations(data.recommendations || []);
      })
      .catch(err => console.error("Error fetching recommendations: ", err))
      .finally(() => setLoading(false));
  }, []);

  const getScoreColor = (score: number) => {
    if (score >= 85) return "from-green-500 to-green-600";
    if (score >= 70) return "from-yellow-500 to-yellow-600";
    return "from-red-500 to-red-600";
  };

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
            <div className="flex items-center gap-3 mb-2">
              <Sparkles className="w-8 h-8 text-purple-400" />
              <h1 className="text-3xl font-bold text-white">AI Recommendations</h1>
            </div>
            <p className="text-gray-400">Top locations curated by AI based on your business needs</p>
          </div>

          {/* Recommendations List */}
          <div className="space-y-6">
            {loading ? (
              <div className="flex flex-col items-center justify-center py-20 space-y-4">
                 <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500"></div>
                 <p className="text-gray-400">Loading AI Recommendations...</p>
              </div>
            ) : recommendations.length === 0 ? (
              <p className="text-gray-400 text-center py-10">No recommendations found.</p>
            ) : (
              recommendations.map((location, index) => (
                <div
                  key={location.id || index}
                className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-6 hover:border-purple-500/50 transition-all"
              >
                <div className="flex flex-col lg:flex-row gap-6">
                  {/* Left: Map Preview */}
                  <div className="lg:w-64 h-48 rounded-xl bg-gradient-to-br from-gray-800 to-gray-900 relative overflow-hidden flex-shrink-0">
                    {/* Mock Map */}
                    <div
                      className="absolute inset-0 opacity-20"
                      style={{
                        backgroundImage: `
                          linear-gradient(rgba(124, 58, 237, 0.3) 1px, transparent 1px),
                          linear-gradient(90deg, rgba(124, 58, 237, 0.3) 1px, transparent 1px)
                        `,
                        backgroundSize: "30px 30px",
                      }}
                    ></div>
                    <div className="absolute inset-0 flex items-center justify-center">
                      <div className={`w-16 h-16 rounded-full bg-gradient-to-r ${getScoreColor(location.score)} flex items-center justify-center shadow-2xl`}>
                        <MapPin className="w-8 h-8 text-white" />
                      </div>
                    </div>
                    {/* Rank Badge */}
                    {index === 0 && (
                      <div className="absolute top-3 left-3 px-3 py-1 rounded-full bg-gradient-to-r from-purple-600 to-blue-600 text-white text-xs font-bold">
                        #1 BEST MATCH
                      </div>
                    )}
                    {index === 1 && (
                      <div className="absolute top-3 left-3 px-3 py-1 rounded-full bg-white/20 text-white text-xs font-bold">
                        #2
                      </div>
                    )}
                    {index === 2 && (
                      <div className="absolute top-3 left-3 px-3 py-1 rounded-full bg-white/20 text-white text-xs font-bold">
                        #3
                      </div>
                    )}
                  </div>

                  {/* Right: Details */}
                  <div className="flex-1">
                    {/* Title and Score */}
                    <div className="flex items-start justify-between mb-4">
                      <div>
                        <h3 className="text-2xl font-bold text-white mb-1">{location.name}</h3>
                        <p className="text-xs text-purple-400 mb-2 flex items-center gap-1">
                          <MapPin className="w-3 h-3" />
                          {location.city}
                        </p>
                        <p className="text-gray-300 text-sm">{location.reason}</p>
                      </div>
                      <div className="text-right">
                        <div className="text-4xl font-bold bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">
                          {location.score}
                        </div>
                        <div className="text-xs text-gray-400">Score</div>
                      </div>
                    </div>

                    {/* Key Metrics */}
                    <div className="grid grid-cols-3 gap-4 mb-4">
                      {location.keyMetrics?.map((metric: { label: string; value: number | string }) => (
                        <div key={metric.label} className="backdrop-blur-md bg-white/5 rounded-xl p-3 border border-white/10">
                          <div className="text-sm text-gray-400 mb-1">{metric.label}</div>
                          <div className="flex items-end gap-1">
                            <div className="text-2xl font-bold text-white">{metric.value}</div>
                            <div className="text-gray-400 mb-1">%</div>
                          </div>
                        </div>
                      ))}
                    </div>

                    {/* AI Insight */}
                    <div className="backdrop-blur-md bg-gradient-to-r from-purple-600/10 to-blue-600/10 border border-purple-500/20 rounded-xl p-4 mb-4">
                      <div className="flex items-center gap-2 mb-2">
                        <TrendingUp className="w-4 h-4 text-purple-400" />
                        <span className="text-sm font-medium text-purple-400">Why recommended</span>
                      </div>
                      <p className="text-sm text-gray-300">{location.aiInsight}</p>
                    </div>

                    {/* Actions */}
                    <div className="flex gap-3">
                      <Button
                        onClick={() => navigate("/dashboard")}
                        className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white"
                      >
                        <MapPin className="w-4 h-4 mr-2" />
                        View on Map
                      </Button>
                      <Button
                        onClick={() => navigate("/reports")}
                        variant="outline"
                        className="bg-white/5 border-white/10 text-white hover:bg-white/10"
                      >
                        <ExternalLink className="w-4 h-4 mr-2" />
                        Full Analysis
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            )))}
          </div>

          {/* Action Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
            <div className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-6">
              <h3 className="text-lg font-bold text-white mb-2">Need More Options?</h3>
              <p className="text-gray-400 text-sm mb-4">
                Explore additional locations that might fit your specific criteria
              </p>
              <Button
                onClick={() => navigate("/")}
                className="bg-white/10 border border-white/20 text-white hover:bg-white/20"
              >
                Explore Map
              </Button>
            </div>

            <div className="backdrop-blur-xl bg-gradient-to-br from-purple-600/20 to-blue-600/20 border border-purple-500/30 rounded-2xl p-6">
              <h3 className="text-lg font-bold text-white mb-2">Compare Top 3</h3>
              <p className="text-gray-400 text-sm mb-4">
                See side-by-side comparison of all recommended locations
              </p>
              <Button
                onClick={() => navigate("/compare")}
                className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white"
              >
                Compare Now
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}