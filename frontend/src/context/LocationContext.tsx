import { createContext, useContext, useState, ReactNode } from "react";
import type { LocationData } from "../app/components/dashboard/Dashboard";

type LocationContextType = {
  selectedLocation: LocationData | null;
  setSelectedLocation: (loc: LocationData | null) => void;
  businessType: string;
  setBusinessType: (type: string) => void;
  weights: { population: number; accessibility: number; competition: number };
  setWeights: (w: any) => void;
};

const LocationContext = createContext<LocationContextType>({
  selectedLocation: null,
  setSelectedLocation: () => {},
  businessType: "restaurant",
  setBusinessType: () => {},
  weights: { population: 50, accessibility: 50, competition: 50 },
  setWeights: () => {},
});

export function LocationProvider({ children }: { children: ReactNode }) {
  const [selectedLocation, setSelectedLocation] = useState<LocationData | null>(null);
  const [businessType, setBusinessType] = useState("restaurant");
  const [weights, setWeights] = useState({ population: 50, accessibility: 50, competition: 50 });

  return (
    <LocationContext.Provider value={{
      selectedLocation, setSelectedLocation,
      businessType, setBusinessType,
      weights, setWeights,
    }}>
      {children}
    </LocationContext.Provider>
  );
}

export const useLocationContext = () => useContext(LocationContext);
