import { useNavigate, useLocation } from "react-router";
import {
  LayoutDashboard,
  GitCompare,
  Lightbulb,
  FileText,
  Settings,
  LogOut,
  User,
  MapPin,
  Bot,
} from "lucide-react";
import { Button } from "../ui/button";
import { Slider } from "../ui/slider";

export type Weights = {
  population: number;
  accessibility: number;
  competition: number;
};

type SidebarProps = {
  weights?: Weights;
  onWeightChange?: (weights: Weights) => void;
};

export function Sidebar({ weights, onWeightChange }: SidebarProps = {}) {
  const navigate = useNavigate();
  const location = useLocation();

  const navItems = [
    { icon: LayoutDashboard, label: "Dashboard", path: "/dashboard" },
    { icon: GitCompare, label: "Compare Locations", path: "/compare" },
    { icon: Lightbulb, label: "Recommendations", path: "/recommendations" },
    { icon: FileText, label: "Reports", path: "/reports" },
    { icon: Settings, label: "Settings", path: "/settings" },
  ];

  const isActive = (path: string) => location.pathname === path;

  const handleLogout = () => {
    navigate("/login");
  };

  return (
    <div
      className="w-60 h-full flex flex-col"
      style={{
        background: "rgba(8,12,24,0.95)",
        backdropFilter: "blur(20px)",
        borderRight: "1px solid rgba(255,255,255,0.08)",
      }}
    >
      {/* Logo */}
      <div className="p-5 border-b border-white/8">
        <div className="flex items-center gap-3">
          <div
            className="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0"
            style={{
              background: "linear-gradient(135deg, #7c3aed, #2563eb)",
              boxShadow: "0 4px 16px rgba(124,58,237,0.4)",
            }}
          >
            <MapPin className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-white leading-tight">GeoVision AI</h2>
            <p className="text-xs text-gray-500">Site Analyzer</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-3 space-y-1">
        <p className="text-xs text-gray-600 font-semibold px-3 py-2 uppercase tracking-wider">
          Navigation
        </p>
        {navItems.map((item) => {
          const Icon = item.icon;
          const active = isActive(item.path);

          return (
            <button
              key={item.label}
              onClick={() => navigate(item.path)}
              className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all text-left"
              style={{
                background: active
                  ? "linear-gradient(135deg, rgba(124,58,237,0.3), rgba(37,99,235,0.3))"
                  : "transparent",
                border: active ? "1px solid rgba(124,58,237,0.3)" : "1px solid transparent",
                color: active ? "#fff" : "rgba(156,163,175,1)",
                boxShadow: active ? "0 2px 12px rgba(124,58,237,0.2)" : "none",
              }}
            >
              <Icon
                className="w-4 h-4 flex-shrink-0"
                style={{ color: active ? "#a78bfa" : "rgba(107,114,128,1)" }}
              />
              <span className="text-sm font-medium">{item.label}</span>
              {active && (
                <div
                  className="ml-auto w-1.5 h-1.5 rounded-full"
                  style={{ background: "#a78bfa" }}
                />
              )}
            </button>
          );
        })}
      </nav>

      {/* Weights / Personalization if props are provided */}
      {weights && onWeightChange && (
        <div className="px-3 pb-3 space-y-3">
          <p className="text-xs text-gray-600 font-semibold px-1 uppercase tracking-wider">
            Scoring Weights
          </p>
          <div className="space-y-4 px-1">
            <div className="space-y-2">
              <div className="flex justify-between text-xs">
                <span className="text-gray-400">Population</span>
                <span className="text-purple-400">{weights.population}</span>
              </div>
              <Slider
                value={[weights.population]}
                max={100}
                step={1}
                onValueChange={(val) => onWeightChange({ ...weights, population: val[0] })}
              />
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-xs">
                <span className="text-gray-400">Accessibility</span>
                <span className="text-purple-400">{weights.accessibility}</span>
              </div>
              <Slider
                value={[weights.accessibility]}
                max={100}
                step={1}
                onValueChange={(val) => onWeightChange({ ...weights, accessibility: val[0] })}
              />
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-xs">
                <span className="text-gray-400">Competition</span>
                <span className="text-purple-400">{weights.competition}</span>
              </div>
              <Slider
                value={[weights.competition]}
                max={100}
                step={1}
                onValueChange={(val) => onWeightChange({ ...weights, competition: val[0] })}
              />
            </div>
          </div>
        </div>
      )}

      {/* AI Assistant quick link */}
      <div className="px-3 pb-3">
        <div
          className="rounded-xl p-3 cursor-pointer transition-all hover:scale-[1.02]"
          style={{
            background: "linear-gradient(135deg, rgba(124,58,237,0.15), rgba(37,99,235,0.15))",
            border: "1px solid rgba(124,58,237,0.2)",
          }}
        >
          <div className="flex items-center gap-2 mb-1">
            <Bot className="w-4 h-4 text-purple-400" />
            <span className="text-xs font-semibold text-purple-300">AI Assistant</span>
          </div>
          <p className="text-xs text-gray-500 leading-relaxed">
            Ask GeoVision AI to find the best locations for your business.
          </p>
        </div>
      </div>

      {/* User Profile */}
      <div className="p-3 border-t border-white/8 space-y-2">
        <div
          className="flex items-center gap-3 p-3 rounded-xl"
          style={{ background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.06)" }}
        >
          <div
            className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0"
            style={{ background: "linear-gradient(135deg, #7c3aed, #2563eb)" }}
          >
            <User className="w-4 h-4 text-white" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-xs font-semibold text-white truncate">Guest User</p>
            <p className="text-xs text-gray-500">Standard Plan</p>
          </div>
          <div className="w-2 h-2 rounded-full bg-green-500 flex-shrink-0" style={{ boxShadow: "0 0 6px rgba(34,197,94,0.6)" }} />
        </div>

        <Button
          onClick={handleLogout}
          variant="outline"
          className="w-full text-xs bg-transparent border-white/10 text-gray-400 hover:bg-red-600/20 hover:text-red-400 hover:border-red-600/40 transition-all"
        >
          <LogOut className="w-3.5 h-3.5 mr-2" />
          Sign Out
        </Button>
      </div>
    </div>
  );
}
