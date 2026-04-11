import { Sidebar } from "../dashboard/Sidebar";
import { ArrowLeft, User, Bell, Shield, MapPin, CreditCard, Globe, Save } from "lucide-react";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Label } from "../ui/label";
import { Switch } from "../ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../ui/select";
import { useNavigate } from "react-router";
import { useState } from "react";

export function Settings() {
  const navigate = useNavigate();
  const [notifications, setNotifications] = useState({
    email: true,
    push: true,
    reports: false,
    recommendations: true,
  });

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
              Back to Dashboard
            </Button>
            <h1 className="text-3xl font-bold text-white mb-2">Settings</h1>
            <p className="text-gray-400">Manage your account and preferences</p>
          </div>

          <div className="max-w-4xl space-y-6">
            {/* Profile Settings */}
            <div className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-6">
              <div className="flex items-center gap-3 mb-6">
                <User className="w-5 h-5 text-purple-400" />
                <h2 className="text-xl font-bold text-white">Profile Settings</h2>
              </div>
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="firstName" className="text-gray-300">First Name</Label>
                    <Input
                      id="firstName"
                      defaultValue="John"
                      className="mt-2 bg-white/5 border-white/10 text-white"
                    />
                  </div>
                  <div>
                    <Label htmlFor="lastName" className="text-gray-300">Last Name</Label>
                    <Input
                      id="lastName"
                      defaultValue="Doe"
                      className="mt-2 bg-white/5 border-white/10 text-white"
                    />
                  </div>
                </div>
                <div>
                  <Label htmlFor="email" className="text-gray-300">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    defaultValue="john.doe@example.com"
                    className="mt-2 bg-white/5 border-white/10 text-white"
                  />
                </div>
                <div>
                  <Label htmlFor="company" className="text-gray-300">Company</Label>
                  <Input
                    id="company"
                    defaultValue="Acme Corp"
                    className="mt-2 bg-white/5 border-white/10 text-white"
                  />
                </div>
              </div>
            </div>

            {/* Notifications */}
            <div className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-6">
              <div className="flex items-center gap-3 mb-6">
                <Bell className="w-5 h-5 text-blue-400" />
                <h2 className="text-xl font-bold text-white">Notifications</h2>
              </div>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 rounded-xl bg-white/5">
                  <div>
                    <p className="text-white font-medium">Email Notifications</p>
                    <p className="text-sm text-gray-400">Receive updates via email</p>
                  </div>
                  <Switch
                    checked={notifications.email}
                    onCheckedChange={(checked) =>
                      setNotifications({ ...notifications, email: checked })
                    }
                  />
                </div>
                <div className="flex items-center justify-between p-4 rounded-xl bg-white/5">
                  <div>
                    <p className="text-white font-medium">Push Notifications</p>
                    <p className="text-sm text-gray-400">Get notified about important updates</p>
                  </div>
                  <Switch
                    checked={notifications.push}
                    onCheckedChange={(checked) =>
                      setNotifications({ ...notifications, push: checked })
                    }
                  />
                </div>
                <div className="flex items-center justify-between p-4 rounded-xl bg-white/5">
                  <div>
                    <p className="text-white font-medium">Report Generation</p>
                    <p className="text-sm text-gray-400">Notify when reports are ready</p>
                  </div>
                  <Switch
                    checked={notifications.reports}
                    onCheckedChange={(checked) =>
                      setNotifications({ ...notifications, reports: checked })
                    }
                  />
                </div>
                <div className="flex items-center justify-between p-4 rounded-xl bg-white/5">
                  <div>
                    <p className="text-white font-medium">AI Recommendations</p>
                    <p className="text-sm text-gray-400">Get AI-powered location suggestions</p>
                  </div>
                  <Switch
                    checked={notifications.recommendations}
                    onCheckedChange={(checked) =>
                      setNotifications({ ...notifications, recommendations: checked })
                    }
                  />
                </div>
              </div>
            </div>

            {/* Default Preferences */}
            <div className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-6">
              <div className="flex items-center gap-3 mb-6">
                <MapPin className="w-5 h-5 text-green-400" />
                <h2 className="text-xl font-bold text-white">Default Preferences</h2>
              </div>
              <div className="space-y-4">
                <div>
                  <Label htmlFor="businessType" className="text-gray-300">Default Business Type</Label>
                  <Select defaultValue="restaurant">
                    <SelectTrigger id="businessType" className="mt-2 bg-white/5 border-white/10 text-white">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-gray-900 border-white/20">
                      <SelectItem value="restaurant">🍽️ Restaurant</SelectItem>
                      <SelectItem value="warehouse">📦 Warehouse</SelectItem>
                      <SelectItem value="ev-station">⚡ EV Station</SelectItem>
                      <SelectItem value="retail">🛍️ Retail Store</SelectItem>
                      <SelectItem value="office">🏢 Office Space</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="region" className="text-gray-300">Default Region</Label>
                  <Select defaultValue="north-america">
                    <SelectTrigger id="region" className="mt-2 bg-white/5 border-white/10 text-white">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-gray-900 border-white/20">
                      <SelectItem value="north-america">North America</SelectItem>
                      <SelectItem value="europe">Europe</SelectItem>
                      <SelectItem value="asia">Asia</SelectItem>
                      <SelectItem value="australia">Australia</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="mapStyle" className="text-gray-300">Map Style</Label>
                  <Select defaultValue="dark">
                    <SelectTrigger id="mapStyle" className="mt-2 bg-white/5 border-white/10 text-white">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-gray-900 border-white/20">
                      <SelectItem value="dark">Dark</SelectItem>
                      <SelectItem value="light">Light</SelectItem>
                      <SelectItem value="satellite">Satellite</SelectItem>
                      <SelectItem value="streets">Streets</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </div>

            {/* Security */}
            <div className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-6">
              <div className="flex items-center gap-3 mb-6">
                <Shield className="w-5 h-5 text-red-400" />
                <h2 className="text-xl font-bold text-white">Security</h2>
              </div>
              <div className="space-y-4">
                <div>
                  <Label htmlFor="currentPassword" className="text-gray-300">Current Password</Label>
                  <Input
                    id="currentPassword"
                    type="password"
                    placeholder="••••••••"
                    className="mt-2 bg-white/5 border-white/10 text-white"
                  />
                </div>
                <div>
                  <Label htmlFor="newPassword" className="text-gray-300">New Password</Label>
                  <Input
                    id="newPassword"
                    type="password"
                    placeholder="••••••••"
                    className="mt-2 bg-white/5 border-white/10 text-white"
                  />
                </div>
                <div>
                  <Label htmlFor="confirmPassword" className="text-gray-300">Confirm New Password</Label>
                  <Input
                    id="confirmPassword"
                    type="password"
                    placeholder="••••••••"
                    className="mt-2 bg-white/5 border-white/10 text-white"
                  />
                </div>
                <Button
                  variant="outline"
                  className="bg-white/5 border-white/10 text-white hover:bg-white/10"
                >
                  Update Password
                </Button>
              </div>
            </div>

            {/* Subscription */}
            <div className="backdrop-blur-xl bg-gradient-to-br from-purple-600/20 to-blue-600/20 border border-purple-500/30 rounded-2xl p-6">
              <div className="flex items-center gap-3 mb-6">
                <CreditCard className="w-5 h-5 text-yellow-400" />
                <h2 className="text-xl font-bold text-white">Subscription & Billing</h2>
              </div>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 rounded-xl bg-white/10">
                  <div>
                    <p className="text-white font-bold text-lg">Pro Plan</p>
                    <p className="text-sm text-gray-300">Unlimited analyses • Advanced AI • Priority support</p>
                  </div>
                  <div className="text-right">
                    <p className="text-2xl font-bold text-white">$99</p>
                    <p className="text-xs text-gray-400">per month</p>
                  </div>
                </div>
                <div className="flex gap-3">
                  <Button
                    variant="outline"
                    className="flex-1 bg-white/5 border-white/10 text-white hover:bg-white/10"
                  >
                    Change Plan
                  </Button>
                  <Button
                    variant="outline"
                    className="flex-1 bg-white/5 border-white/10 text-white hover:bg-white/10"
                  >
                    Billing History
                  </Button>
                </div>
              </div>
            </div>

            {/* Language & Region */}
            <div className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-6">
              <div className="flex items-center gap-3 mb-6">
                <Globe className="w-5 h-5 text-cyan-400" />
                <h2 className="text-xl font-bold text-white">Language & Region</h2>
              </div>
              <div className="space-y-4">
                <div>
                  <Label htmlFor="language" className="text-gray-300">Language</Label>
                  <Select defaultValue="english">
                    <SelectTrigger id="language" className="mt-2 bg-white/5 border-white/10 text-white">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-gray-900 border-white/20">
                      <SelectItem value="english">English</SelectItem>
                      <SelectItem value="spanish">Spanish</SelectItem>
                      <SelectItem value="french">French</SelectItem>
                      <SelectItem value="german">German</SelectItem>
                      <SelectItem value="chinese">Chinese</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="timezone" className="text-gray-300">Timezone</Label>
                  <Select defaultValue="est">
                    <SelectTrigger id="timezone" className="mt-2 bg-white/5 border-white/10 text-white">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-gray-900 border-white/20">
                      <SelectItem value="est">Eastern Time (ET)</SelectItem>
                      <SelectItem value="cst">Central Time (CT)</SelectItem>
                      <SelectItem value="mst">Mountain Time (MT)</SelectItem>
                      <SelectItem value="pst">Pacific Time (PT)</SelectItem>
                      <SelectItem value="utc">UTC</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </div>

            {/* Save Button */}
            <div className="flex gap-4 justify-end pb-8">
              <Button
                variant="outline"
                className="bg-white/5 border-white/10 text-white hover:bg-white/10"
              >
                Cancel
              </Button>
              <Button className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white">
                <Save className="w-4 h-4 mr-2" />
                Save Changes
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}