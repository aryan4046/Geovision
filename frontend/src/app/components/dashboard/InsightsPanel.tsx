import { X, Download, TrendingUp, TrendingDown, Zap, MapPin } from "lucide-react";
import { Button } from "../ui/button";
import { Progress } from "../ui/progress";
import { LocationData } from "./Dashboard";
import { useNavigate } from "react-router";

type InsightsPanelProps = {
  location: LocationData;
  competitorImpact?: any;
};

export function InsightsPanel({ location, competitorImpact }: InsightsPanelProps) {
  const navigate = useNavigate();

  const getScoreColor = (score: number) => {
    if (score >= 85) return "text-green-500";
    if (score >= 70) return "text-yellow-500";
    return "text-red-500";
  };

  const getScoreGradient = (score: number) => {
    if (score >= 85) return "from-green-500 to-green-600";
    if (score >= 70) return "from-yellow-500 to-yellow-600";
    return "from-red-500 to-red-600";
  };

  return (
    <div className="w-96 h-full overflow-y-auto flex flex-col" style={{ background: "rgba(8,12,24,0.97)", backdropFilter: "blur(24px)", borderLeft: "1px solid rgba(255,255,255,0.08)", boxShadow: "-8px 0 40px rgba(0,0,0,0.5)" }}>
      <div className="p-6 space-y-6">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div>
            <h3 className="text-xl font-bold text-white">{location.name}</h3>
            <p className="text-sm text-gray-400 mt-1 flex items-center gap-1">
              <MapPin className="w-3 h-3 text-purple-400" />
              {location.lat.toFixed(4)}°N, {location.lng.toFixed(4)}°E · India
            </p>
          </div>
        </div>

        {/* Site Readiness Score */}
        <div className="backdrop-blur-md bg-white/5 border border-white/10 rounded-xl p-6">
          <h4 className="text-sm font-medium text-gray-300 mb-4">Site Readiness Score</h4>
          <div className="flex items-center justify-center mb-4">
            <div className="relative">
              <svg className="w-32 h-32 transform -rotate-90">
                <circle
                  cx="64"
                  cy="64"
                  r="56"
                  stroke="rgba(255,255,255,0.1)"
                  strokeWidth="8"
                  fill="none"
                />
                <circle
                  cx="64"
                  cy="64"
                  r="56"
                  stroke="url(#scoreGradient)"
                  strokeWidth="8"
                  fill="none"
                  strokeDasharray={`${(location.score / 100) * 351.86} 351.86`}
                  strokeLinecap="round"
                />
                <defs>
                  <linearGradient id="scoreGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stopColor="#7C3AED" />
                    <stop offset="100%" stopColor="#3B82F6" />
                  </linearGradient>
                </defs>
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="text-center">
                  <p className={`text-3xl font-bold ${getScoreColor(location.score)}`}>
                    {location.score}
                  </p>
                  <p className="text-xs text-gray-400">out of 100</p>
                </div>
              </div>
            </div>
          </div>
          <p className="text-xs text-center text-gray-400">
            {location.score >= 85
              ? "Excellent location for your business"
              : location.score >= 70
              ? "Good location with some improvements needed"
              : "Consider other locations or improvements"}
          </p>
        </div>

        {/* Score Breakdown */}
        <div className="backdrop-blur-md bg-white/5 border border-white/10 rounded-xl p-6">
          <h4 className="text-sm font-medium text-gray-300 mb-4">Score Breakdown</h4>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between mb-2">
                <span className="text-sm text-gray-300">Population Density</span>
                <span className="text-sm font-medium text-white">{(location as any).rawMetrics?.population ? Math.round((location as any).rawMetrics.population).toLocaleString() + ' / sqkm' : `${location.population}%`}</span>
              </div>
              <Progress value={location.population > 100 ? 100 : location.population} className="h-2" />
            </div>
            <div>
              <div className="flex justify-between mb-2">
                <span className="text-sm text-gray-300">Accessibility</span>
                <span className="text-sm font-medium text-white">{location.accessibility}%</span>
              </div>
              <Progress value={location.accessibility} className="h-2" />
            </div>
            {/* Added real India census stats context if available */}
            {(location as any).rawMetrics?.state_census?.total_population > 0 && (
              <div className="mt-4 pt-3 border-t border-white/10">
                <span className="text-xs text-purple-400 font-semibold mb-2 block uppercase tracking-wide">
                  State Census ({(location as any).rawMetrics.state_census.state})
                </span>
                <div className="grid grid-cols-2 gap-2">
                  <div className="bg-white/5 p-2 rounded-lg">
                     <p className="text-[10px] text-gray-400 uppercase">Population</p>
                     <p className="text-xs font-bold text-white">{(location as any).rawMetrics.state_census.total_population.toLocaleString()}</p>
                  </div>
                  <div className="bg-white/5 p-2 rounded-lg">
                     <p className="text-[10px] text-gray-400 uppercase">Urban</p>
                     <p className="text-xs font-bold text-white">{(location as any).rawMetrics.state_census.urban_population.toLocaleString()}</p>
                  </div>
                  <div className="bg-white/5 p-2 rounded-lg">
                     <p className="text-[10px] text-gray-400 uppercase">Density</p>
                     <p className="text-xs font-bold text-white">{(location as any).rawMetrics.state_census.density_sqkm.toLocaleString()} / km²</p>
                  </div>
                  <div className="bg-white/5 p-2 rounded-lg">
                     <p className="text-[10px] text-gray-400 uppercase">Sex Ratio</p>
                     <p className="text-xs font-bold text-white">{(location as any).rawMetrics.state_census.sex_ratio}</p>
                  </div>
                </div>
              </div>
            )}
            <div>
              <div className="flex justify-between mb-2">
                <span className="text-sm text-gray-300">
                  Low Competition
                  <span className="text-xs text-gray-500 ml-1">(higher = fewer rivals)</span>
                </span>
                <span className="text-sm font-medium text-white">{location.competition}%</span>
              </div>
              <Progress value={location.competition} className="h-2" />
            </div>
            <div>
              <div className="flex justify-between mb-2">
                <span className="text-sm text-gray-300">Footfall Potential</span>
                <span className="text-sm font-medium text-white">{location.pois}%</span>
              </div>
              <Progress value={location.pois} className="h-2" />
            </div>
          </div>
        </div>

        {/* AI Explanation */}
        <div className="backdrop-blur-md bg-white/5 border border-white/10 rounded-xl p-6">
          <h4 className="text-sm font-medium text-gray-300 mb-4">🧠 AI Analysis</h4>

          {/* Strengths */}
          <div className="mb-4">
            <div className="flex items-center gap-2 mb-2">
              <TrendingUp className="w-4 h-4 text-green-500" />
              <span className="text-sm font-medium text-white">Strengths</span>
            </div>
            <ul className="space-y-2">
              {location.strengths.map((strength, index) => (
                <li key={index} className="text-sm text-gray-300 flex items-start gap-2">
                  <span className="text-green-500">✓</span>
                  <span>{strength}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Weaknesses */}
          <div className="mb-4">
            <div className="flex items-center gap-2 mb-2">
              <TrendingDown className="w-4 h-4 text-red-500" />
              <span className="text-sm font-medium text-white">Weaknesses</span>
            </div>
            <ul className="space-y-2">
              {location.weaknesses.map((weakness, index) => (
                <li key={index} className="text-sm text-gray-300 flex items-start gap-2">
                  <span className="text-red-500">✗</span>
                  <span>{weakness}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Opportunities */}
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Zap className="w-4 h-4 text-yellow-500" />
              <span className="text-sm font-medium text-white">Opportunities</span>
            </div>
            <ul className="space-y-2">
              {location.opportunities.map((opportunity, index) => (
                <li key={index} className="text-sm text-gray-300 flex items-start gap-2">
                  <span className="text-yellow-500">⚡</span>
                  <span>{opportunity}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Competitor Impact */}
        {competitorImpact && (
          <div className="backdrop-blur-md bg-white/5 border border-white/10 rounded-xl p-6 mb-4">
            <h4 className="text-sm font-medium text-gray-300 mb-4">⚔️ Competitor Impact</h4>
            <div className="space-y-4">
              <div className="flex justify-between items-center text-sm">
                <span className="text-gray-300">Competitors Nearby</span>
                <span className="font-bold text-white">{competitorImpact.count || 0}</span>
              </div>
              <div className="flex justify-between items-center text-sm">
                <span className="text-gray-300">Market Saturation</span>
                <span className="font-bold text-white">{competitorImpact.saturation || 'Low'}%</span>
              </div>
              {competitorImpact.riskLevel && (
                <div className="flex justify-between items-center text-sm mt-2">
                  <span className="text-gray-300">Risk Level</span>
                  <span className={`font-bold px-2 py-1 rounded-full text-xs ${
                    competitorImpact.riskLevel === 'High' ? 'bg-red-500/20 text-red-400' :
                    competitorImpact.riskLevel === 'Medium' ? 'bg-yellow-500/20 text-yellow-400' :
                    'bg-green-500/20 text-green-400'
                  }`}>
                    {competitorImpact.riskLevel}
                  </span>
                </div>
              )}
              {/* Added Real Competitor Names Display */}
              {(location as any).rawMetrics?.competitor_names?.length > 0 && (
                <div className="mt-3 pt-3 border-t border-white/10">
                  <span className="text-xs text-gray-400 mb-1 block">Known Competitors:</span>
                  <div className="flex flex-wrap gap-1">
                    {(location as any).rawMetrics.competitor_names.map((name: string, i: number) => (
                      <span key={i} className="text-xs px-2 py-0.5 rounded-md bg-white/10 text-gray-300">
                        {name}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="space-y-3">
          <Button
            onClick={() => navigate("/reports")}
            className="w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white"
          >
            <Download className="w-4 h-4 mr-2" />
            Generate Report
          </Button>
          <Button
            onClick={() => navigate("/compare")}
            variant="outline"
            className="w-full bg-white/5 border-white/10 text-white hover:bg-white/10"
          >
            Compare Locations
          </Button>
        </div>
      </div>
    </div>
  );
}