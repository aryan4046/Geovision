import { useState, useCallback } from "react";
import { apiService } from "../services/apiService";
import { LocationData } from "../app/components/dashboard/Dashboard";

export const useLocationAnalysis = () => {
  const [selectedLocation, setSelectedLocation] = useState<LocationData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [competitorImpact, setCompetitorImpact] = useState<any>(null);

  /**
   * Analyze a clicked location — calls /get-score (which bundles explanation)
   * and /competitor-impact in parallel.
   * Returns the built LocationData so callers can sync it to context.
   */
  const analyzeLocation = useCallback(async (
    lat: number, lng: number, weights: any, businessType: string
  ): Promise<LocationData | null> => {
    setLoading(true);
    setError(null);
    try {
      // Normalize slider weights (0-100) → (0-1) for backend
      const normalizedWeights = {
        population:    (weights.population    ?? 50) / 100,
        competition:   (weights.competition   ?? 50) / 100,
        accessibility: (weights.accessibility ?? 50) / 100,
      };

      // POST /get-score returns { score, factors, grade, explanation, business_type }
      const [scoreData, impactData] = await Promise.all([
        apiService.fetchScore(lat, lng, normalizedWeights, businessType),
        apiService.fetchCompetitorImpact(lat, lng).catch(() => null),
      ]);

      if (!scoreData) throw new Error("Unable to fetch score for this location.");

      setCompetitorImpact(impactData);

      const factors     = scoreData.factors     || {};
      const explanation = scoreData.explanation || {};
      const rawMetrics  = scoreData.raw_metrics || {};

      const loc: LocationData = {
        id:            `${lat}-${lng}`,
        name:          scoreData.location_name || `Location (${lat.toFixed(4)}, ${lng.toFixed(4)})`,
        lat,
        lng,
        score:         scoreData.score ?? 0,
        // Replace percentages with exact count thresholds where applicable
        population:    Math.round(rawMetrics.population || (factors.population ?? 0.5) * 100000),
        accessibility: Math.round((factors.accessibility ?? 0) * 100),
        competition:   Math.round((factors.competition   ?? 0) * 100),
        pois:          Math.round((factors.footfall      ?? 0) * 100),
        strengths:     explanation.strengths     || [],
        weaknesses:    explanation.weaknesses    || [],
        opportunities: explanation.opportunities || [],
      };

      // Expose the raw data to be used in UI components (like InsightsPanel)
      (loc as any).rawMetrics = rawMetrics;

      setSelectedLocation(loc);
      return loc;
    } catch (err: any) {
      setError(err.message || "Failed to analyze location.");
      setSelectedLocation(null);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  return { selectedLocation, setSelectedLocation, loading, error, analyzeLocation, competitorImpact };
};