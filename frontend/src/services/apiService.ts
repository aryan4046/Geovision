import { API_ENDPOINTS } from "../config/apiConfig";

// Assuming backend runs on a relative proxy in Vite via base URL, or hardcoded for dev
const BASE_URL = (import.meta as any).env?.VITE_API_URL || "http://127.0.0.1:8000";

export const apiService = {
  async fetchScore(lat: number, lng: number, weights: any, business_type: string) {
    const response = await fetch(`${BASE_URL}${API_ENDPOINTS.GET_SCORE}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ lat, lng, business_type, weights }),
    });
    if (!response.ok) throw new Error("Failed to fetch score");
    return response.json();
  },

  async fetchExplanation(lat: number, lng: number) {
    const response = await fetch(`${BASE_URL}${API_ENDPOINTS.GET_EXPLANATION}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ lat, lng }),
    });
    if (!response.ok) throw new Error("Failed to fetch explanation");
    return response.json();
  },

  async fetchRecommendations() {
    const response = await fetch(`${BASE_URL}${API_ENDPOINTS.GET_RECOMMENDATIONS}`, {
      method: "GET",
    });
    if (!response.ok) throw new Error("Failed to fetch recommendations");
    return response.json();
  },

  async fetchHotspots() {
    const response = await fetch(`${BASE_URL}${API_ENDPOINTS.GET_HOTSPOTS}`, {
      method: "GET",
    });
    if (!response.ok) throw new Error("Failed to fetch hotspots");
    return response.json();
  },

  async fetchCompetitorImpact(lat: number, lng: number) {
    const response = await fetch(`${BASE_URL}${API_ENDPOINTS.COMPETITOR_IMPACT}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ lat, lng }),
    });
    if (!response.ok) throw new Error("Failed to fetch competitor impact");
    return response.json();
  },

  async fetchComparison(loc1: {lat: number, lng: number}, loc2: {lat: number, lng: number}) {
    const response = await fetch(`${BASE_URL}${API_ENDPOINTS.COMPARE}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ location1: loc1, location2: loc2 }),
    });
    if (!response.ok) throw new Error("Failed to fetch comparison");
    return response.json();
  },

  async fetchChat(message: string, context?: any) {
    const response = await fetch(`${BASE_URL}${API_ENDPOINTS.CHAT}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, context }),
    });
    if (!response.ok) throw new Error("Failed to fetch chat");
    return response.json();
  }
};