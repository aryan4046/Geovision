import { createContext, useContext, useState, ReactNode } from "react";
import type { LocationData } from "../app/components/dashboard/Dashboard";

type LocationContextType = {
  selectedLocation: LocationData | null;
  previousLocation: LocationData | null;
  setSelectedLocation: (loc: LocationData | null) => void;
  businessType: string;
  setBusinessType: (type: string) => void;
  weights: { population: number; accessibility: number; competition: number };
  setWeights: (w: any) => void;
};

const LocationContext = createContext<LocationContextType>({
  selectedLocation: null,
  previousLocation: null,
  setSelectedLocation: () => {},
  businessType: "restaurant",
  setBusinessType: () => {},
  weights: { population: 50, accessibility: 50, competition: 50 },
  setWeights: () => {},
});

export function LocationProvider({ children }: { children: ReactNode }) {
  const [selectedLocation, setSelectedLocationState] = useState<LocationData | null>(null);
  const [previousLocation, setPreviousLocation] = useState<LocationData | null>(null);
  const [businessType, setBusinessType] = useState("restaurant");
  const [weights, setWeights] = useState({ population: 50, accessibility: 50, competition: 50 });

  const setSelectedLocation = (loc: LocationData | null) => {
    // If setting a real location and it's different from the current one, push current to previous
    if (loc && selectedLocation && (loc.lat !== selectedLocation.lat || loc.lng !== selectedLocation.lng)) {
      setPreviousLocation(selectedLocation);
    }
    // If loc is null, don't clobber previousLocation so we can still compare
    setSelectedLocationState(loc);
  };

  return (
    <LocationContext.Provider value={{
      selectedLocation, previousLocation, setSelectedLocation,
      businessType, setBusinessType,
      weights, setWeights,
    }}>
      {children}
    </LocationContext.Provider>
  );
}

export const useLocationContext = () => useContext(LocationContext);

