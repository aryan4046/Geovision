import { useState, useCallback } from "react";
import { apiService } from "../services/apiService";
import { LocationData } from "../app/components/dashboard/Dashboard";

export const useLocationAnalysis = () => {
  const [selectedLocation, setSelectedLocation] = useState<LocationData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [competitorImpact, setCompetitorImpact] = useState<any>(null);

  const analyzeLocation = useCallback(async (lat: number, lng: number, weights: any, businessType: string) => {
    setLoading(true);
    setError(null);
    try {
      const [scoreData, explanationData, impactData] = await Promise.all([
        apiService.fetchScore(lat, lng, weights, businessType).catch(() => null),
        apiService.fetchExplanation(lat, lng).catch(() => null),
        apiService.fetchCompetitorImpact(lat, lng).catch(() => null)
      ]);

      if (!scoreData) {
        throw new Error("Unable to fetch score for this location.");
      }

      setCompetitorImpact(impactData);

      setSelectedLocation({
        id: `${lat}-${lng}`,
        name: scoreData.name || `Location (${lat.toFixed(4)}, ${lng.toFixed(4)})`,
        lat,
        lng,
        score: scoreData.score || 0,
        population: scoreData.population || 0,
        accessibility: scoreData.accessibility || 0,
        competition: scoreData.competition || 0,
        pois: scoreData.pois || 0,
        strengths: explanationData?.strengths || ["Analyzing location strengths..."],
        weaknesses: explanationData?.weaknesses || ["Analyzing location weaknesses..."],
        opportunities: explanationData?.opportunities || ["Identifying opportunities..."],
      });
    } catch (err: any) {
      setError(err.message || "Failed to analyze location.");
      setSelectedLocation(null);
    } finally {
      setLoading(false);
    }
  }, []);

  return { selectedLocation, setSelectedLocation, loading, error, analyzeLocation, competitorImpact };
};