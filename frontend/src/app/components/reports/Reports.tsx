import { Sidebar } from "../dashboard/Sidebar";
import { ArrowLeft, Download, MapPin, TrendingUp, TrendingDown, Zap, BarChart3, Users, Store } from "lucide-react";
import { Button } from "../ui/button";
import { useNavigate } from "react-router";
import { Progress } from "../ui/progress";
import { useState, useEffect } from "react";
import { useLocationContext } from "../../../context/LocationContext";
import { apiService } from "../../../services/apiService";

export function Reports() {
  const navigate = useNavigate();
  const { selectedLocation, businessType, weights } = useLocationContext();
  const [reportData, setReportData] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (selectedLocation) {
      setLoading(true);
      // Construct normalized weights
      const normalizedWeights = {
        population: (weights.population ?? 50) / 100,
        competition: (weights.competition ?? 50) / 100,
        accessibility: (weights.accessibility ?? 50) / 100,
      };

      apiService.generateReport(selectedLocation.lat, selectedLocation.lng, businessType, normalizedWeights)
        .then(data => {
          // Map backend response to the structure expected by the report UI
          setReportData({
            location: selectedLocation.name || `Location (${selectedLocation.lat.toFixed(3)}, ${selectedLocation.lng.toFixed(3)})`,
            businessType: businessType.charAt(0).toUpperCase() + businessType.slice(1),
            generatedDate: new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' }),
            score: data.score || 0,
            metrics: {
              population: Math.round((data.factors?.population || 0) * 100),
              accessibility: Math.round((data.factors?.accessibility || 0) * 100),
              competition: Math.round((data.factors?.competition || 0) * 100),
              pois: Math.round((data.factors?.footfall || 0) * 100),
            },
            demographics: {
              avgAge: "28-35 yrs",
              avgIncome: `₹${Math.round((data.factors?.avg_income || 50) * 1000)}k/year`,
              density: `${Math.round((data.factors?.population || 0.5) * 200000)}/sq km`,
              growthRate: "+4.2%",
            },
            strengths: data.explanation?.strengths || [],
            weaknesses: data.explanation?.weaknesses || [],
            opportunities: data.explanation?.opportunities || [],
            financialProjection: {
              estimatedFootTraffic: `${Math.round((data.factors?.footfall || 0.5) * 8000)}/day`,
              peakHours: "12 PM - 3 PM, 6 PM - 9 PM",
              estimatedRevenue: `₹${Math.round((data.score || 50) * 15000)}/month`,
              breakEven: "8-12 Months",
            }
          });
        })
        .catch(err => console.error(err))
        .finally(() => setLoading(false));
    }
  }, [selectedLocation, businessType, weights]);

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
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold text-white mb-2">Site Readiness Report</h1>
                <p className="text-gray-400">
                  {reportData ? `Generated on ${reportData.generatedDate}` : "No report active"}
                </p>
              </div>
              {reportData && (
                <Button className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white">
                  <Download className="w-4 h-4 mr-2" />
                  Export PDF
                </Button>
              )}
            </div>
          </div>

          {/* Report Container */}
          {loading ? (
             <div className="flex flex-col items-center justify-center p-20 text-center bg-white/5 rounded-2xl border border-white/10 backdrop-blur-xl mt-8">
               <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500 mb-6"></div>
               <p className="text-gray-400">Generating Comprehensive Report...</p>
             </div>
          ) : !reportData ? (
             <div className="flex flex-col items-center justify-center p-20 text-center bg-white/5 rounded-2xl border border-white/10 backdrop-blur-xl mt-8">
               <MapPin className="w-16 h-16 text-gray-500 mb-6" />
               <h2 className="text-2xl font-bold text-white mb-2">No Report Generated</h2>
               <p className="text-gray-400 mb-8 max-w-md">
                 Please select a location on the Dashboard to fetch your AI-driven readiness report.
               </p>
               <Button onClick={() => navigate("/dashboard")} className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white px-8 py-6 rounded-xl">
                 <MapPin className="w-5 h-5 mr-2" /> Let's Explore Locations
               </Button>
             </div>
          ) : (
          <div className="max-w-5xl mx-auto space-y-6 mt-8">
            {/* Executive Summary */}
            <div className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-8">
              <h2 className="text-2xl font-bold text-white mb-6">Executive Summary</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <div className="flex items-center gap-3 mb-4">
                    <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-600 to-blue-600 flex items-center justify-center">
                      <MapPin className="w-6 h-6 text-white" />
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-white">{reportData.location}</h3>
                      <p className="text-sm text-gray-400">{reportData.businessType}</p>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-gray-400">Analysis Date:</span>
                      <span className="text-white font-medium">{reportData.generatedDate}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Business Type:</span>
                      <span className="text-white font-medium">{reportData.businessType}</span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center justify-center">
                  <div className="relative">
                    <svg className="w-40 h-40 transform -rotate-90">
                      <circle cx="80" cy="80" r="70" stroke="rgba(255,255,255,0.1)" strokeWidth="10" fill="none" />
                      <circle
                        cx="80"
                        cy="80"
                        r="70"
                        stroke="url(#reportGradient)"
                        strokeWidth="10"
                        fill="none"
                        strokeDasharray={`${(reportData.score / 100) * 439.82} 439.82`}
                        strokeLinecap="round"
                      />
                      <defs>
                        <linearGradient id="reportGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                          <stop offset="0%" stopColor="#7C3AED" />
                          <stop offset="100%" stopColor="#3B82F6" />
                        </linearGradient>
                      </defs>
                    </svg>
                    <div className="absolute inset-0 flex items-center justify-center">
                      <div className="text-center">
                        <p className="text-5xl font-bold text-green-400">{reportData.score}</p>
                        <p className="text-xs text-gray-400">Overall Score</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Score Breakdown */}
            <div className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-8">
              <div className="flex items-center gap-3 mb-6">
                <BarChart3 className="w-6 h-6 text-purple-400" />
                <h2 className="text-xl font-bold text-white">Score Breakdown</h2>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <div className="flex justify-between mb-2">
                    <span className="text-gray-300">Population Density</span>
                    <span className="text-white font-medium">{reportData.metrics.population}%</span>
                  </div>
                  <Progress value={reportData.metrics.population} className="h-3 mb-4" />

                  <div className="flex justify-between mb-2">
                    <span className="text-gray-300">Accessibility</span>
                    <span className="text-white font-medium">{reportData.metrics.accessibility}%</span>
                  </div>
                  <Progress value={reportData.metrics.accessibility} className="h-3" />
                </div>
                <div>
                  <div className="flex justify-between mb-2">
                    <span className="text-gray-300">Low Competition Level</span>
                    <span className="text-white font-medium">{reportData.metrics.competition}%</span>
                  </div>
                  <Progress value={reportData.metrics.competition} className="h-3 mb-4" />

                  <div className="flex justify-between mb-2">
                    <span className="text-gray-300">Footfall Potential</span>
                    <span className="text-white font-medium">{reportData.metrics.pois}%</span>
                  </div>
                  <Progress value={reportData.metrics.pois} className="h-3" />
                </div>
              </div>
            </div>

            {/* Demographics */}
            <div className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-8">
              <div className="flex items-center gap-3 mb-6">
                <Users className="w-6 h-6 text-blue-400" />
                <h2 className="text-xl font-bold text-white">Demographics & Market</h2>
              </div>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="backdrop-blur-md bg-white/5 rounded-xl p-4 border border-white/10">
                  <div className="text-sm text-gray-400 mb-1">Average Age</div>
                  <div className="text-lg font-bold text-white">{reportData.demographics.avgAge}</div>
                </div>
                <div className="backdrop-blur-md bg-white/5 rounded-xl p-4 border border-white/10">
                  <div className="text-sm text-gray-400 mb-1">Avg Income</div>
                  <div className="text-lg font-bold text-white">{reportData.demographics.avgIncome}</div>
                </div>
                <div className="backdrop-blur-md bg-white/5 rounded-xl p-4 border border-white/10">
                  <div className="text-sm text-gray-400 mb-1">Density</div>
                  <div className="text-lg font-bold text-white">{reportData.demographics.density}</div>
                </div>
                <div className="backdrop-blur-md bg-white/5 rounded-xl p-4 border border-white/10">
                  <div className="text-sm text-gray-400 mb-1">Growth Rate</div>
                  <div className="text-lg font-bold text-green-400">{reportData.demographics.growthRate}</div>
                </div>
              </div>
            </div>

            {/* AI Analysis */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Strengths */}
              <div className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-6">
                <div className="flex items-center gap-2 mb-4">
                  <TrendingUp className="w-5 h-5 text-green-500" />
                  <h3 className="text-lg font-bold text-white">Strengths</h3>
                </div>
                <ul className="space-y-3">
                  {reportData.strengths.map((strength: string, index: number) => (
                    <li key={index} className="text-sm text-gray-300 flex items-start gap-2">
                      <span className="text-green-500 mt-0.5">✓</span>
                      <span>{strength}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Weaknesses */}
              <div className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-6">
                <div className="flex items-center gap-2 mb-4">
                  <TrendingDown className="w-5 h-5 text-red-500" />
                  <h3 className="text-lg font-bold text-white">Weaknesses</h3>
                </div>
                <ul className="space-y-3">
                  {reportData.weaknesses.map((weakness: string, index: number) => (
                    <li key={index} className="text-sm text-gray-300 flex items-start gap-2">
                      <span className="text-red-500 mt-0.5">✗</span>
                      <span>{weakness}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Opportunities */}
              <div className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-6">
                <div className="flex items-center gap-2 mb-4">
                  <Zap className="w-5 h-5 text-yellow-500" />
                  <h3 className="text-lg font-bold text-white">Opportunities</h3>
                </div>
                <ul className="space-y-3">
                  {reportData.opportunities.map((opportunity: string, index: number) => (
                    <li key={index} className="text-sm text-gray-300 flex items-start gap-2">
                      <span className="text-yellow-500 mt-0.5">⚡</span>
                      <span>{opportunity}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Financial Projection */}
            <div className="backdrop-blur-xl bg-gradient-to-br from-purple-600/20 to-blue-600/20 border border-purple-500/30 rounded-2xl p-8">
              <div className="flex items-center gap-3 mb-6">
                <Store className="w-6 h-6 text-purple-400" />
                <h2 className="text-xl font-bold text-white">Financial Projection</h2>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-300">Est. Foot Traffic:</span>
                    <span className="text-white font-medium">{reportData.financialProjection.estimatedFootTraffic}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-300">Peak Hours:</span>
                    <span className="text-white font-medium">{reportData.financialProjection.peakHours}</span>
                  </div>
                </div>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-300">Est. Revenue:</span>
                    <span className="text-green-400 font-bold">{reportData.financialProjection.estimatedRevenue}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-300">Break-Even Period:</span>
                    <span className="text-white font-medium">{reportData.financialProjection.breakEven}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Final Recommendation */}
            <div className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-8">
              <h2 className="text-xl font-bold text-white mb-4">Final Recommendation</h2>
              <p className="text-gray-300 mb-4">
                Based on comprehensive AI analysis, <span className="text-purple-400 font-semibold">{reportData.location}</span> is <span className={reportData.score > 70 ? "text-green-400 font-semibold" : "text-yellow-400 font-semibold"}>{reportData.score > 70 ? "highly recommended" : "moderately recommended"}</span> for your {reportData.businessType.toLowerCase()} business. The location scores overall {reportData.score}/100.
              </p>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-4 justify-center pb-8">
              <Button
                onClick={() => navigate("/dashboard")}
                variant="outline"
                className="bg-white/5 border-white/10 text-white hover:bg-white/10"
              >
                <MapPin className="w-4 h-4 mr-2" />
                View on Map
              </Button>
              <Button
                onClick={() => navigate("/compare")}
                variant="outline"
                className="bg-white/5 border-white/10 text-white hover:bg-white/10"
              >
                Compare Locations
              </Button>
            </div>
          </div>
          )}
        </div>
      </div>
    </div>
  );
}