import { Link, useLocation } from "react-router-dom";
import { LayoutDashboard, AlertTriangle, FileText, BarChart3, Car, LogOut, Shield } from "lucide-react";
import { useAuthStore } from "../../store/authStore";

const navItems = [
  { to: "/dashboard", icon: LayoutDashboard, label: "Dashboard" },
  { to: "/violations", icon: AlertTriangle, label: "Violations" },
  { to: "/challans", icon: FileText, label: "Challans" },
  { to: "/analytics", icon: BarChart3, label: "Analytics" },
  { to: "/vehicles", icon: Car, label: "Vehicles" },
];

export default function Sidebar() {
  const location = useLocation();
  const { logout, user } = useAuthStore();

  return (
    <aside className="w-64 min-h-screen bg-slate-900 text-white flex flex-col">
      <div className="p-6 border-b border-slate-700">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 bg-red-500 rounded-lg flex items-center justify-center">
            <Shield size={20} />
          </div>
          <div>
            <p className="font-bold text-sm">VisionPatrol</p>
            <p className="text-xs text-slate-400">AI Traffic Enforcement</p>
          </div>
        </div>
      </div>
      <nav className="flex-1 p-4 space-y-1">
        {navItems.map(({ to, icon: Icon, label }) => {
          const active = location.pathname.startsWith(to);
          return (
            <Link key={to} to={to}
              className={`flex items-center gap-3 px-4 py-3 rounded-lg text-sm transition-all ${
                active ? "bg-red-500 text-white font-medium" : "text-slate-400 hover:bg-slate-800 hover:text-white"
              }`}>
              <Icon size={18} />
              {label}
            </Link>
          );
        })}
      </nav>
      <div className="p-4 border-t border-slate-700">
        <div className="flex items-center gap-3 mb-3 px-2">
          <div className="w-8 h-8 bg-red-500 rounded-full flex items-center justify-center text-sm font-bold">
            {user?.full_name?.[0] || "U"}
          </div>
          <div>
            <p className="text-sm font-medium">{user?.full_name}</p>
            <p className="text-xs text-slate-400 capitalize">{user?.role}</p>
          </div>
        </div>
        <button onClick={logout}
          className="w-full flex items-center gap-3 px-4 py-2 text-sm text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-all">
          <LogOut size={16} /> Logout
        </button>
      </div>
    </aside>
  );
}