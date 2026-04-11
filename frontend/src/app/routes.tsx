import { createBrowserRouter } from "react-router";
import { Login } from "./components/auth/Login";
import { Dashboard } from "./components/dashboard/Dashboard";
import { Compare } from "./components/compare/Compare";
import { Recommendations } from "./components/recommendations/Recommendations";
import { Reports } from "./components/reports/Reports";
import { Settings } from "./components/settings/Settings";

export const router = createBrowserRouter([
  {
    path: "/",
    Component: Login,
  },
  {
    path: "/dashboard",
    Component: Dashboard,
  },
  {
    path: "/login",
    Component: Login,
  },
  {
    path: "/compare",
    Component: Compare,
  },
  {
    path: "/recommendations",
    Component: Recommendations,
  },
  {
    path: "/reports",
    Component: Reports,
  },
  {
    path: "/settings",
    Component: Settings,
  },
]);