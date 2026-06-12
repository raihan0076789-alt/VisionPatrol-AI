import { useEffect, useState } from "react";
import { AlertTriangle, FileText, TrendingUp, IndianRupee, Clock } from "lucide-react";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend } from "recharts";
import StatCard from "../../components/shared/StatCard";
import { analyticsApi } from "../../api/analytics";
import { AnalyticsSummary } from "../../types";

const PIE_COLORS = ["#ef4444", "#f97316", "#eab308", "#ec4899", "#a855f7", "#06b6d4"];
const tooltip = { contentStyle: { backgroundColor: "#1e293b", border: "none", borderRadius: 8 }, labelStyle: { color: "#94a3b8" } };

export default function DashboardPage() {
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [byType, setByType] = useState<{ type: string; count: number }[]>([]);
  const [byDay, setByDay] = useState<{ date: string; count: number }[]>([]);

  useEffect(() => {
    analyticsApi.summary().then(setSummary).catch(console.error);
    analyticsApi.byType(30).then(setByType).catch(console.error);
    analyticsApi.byDay(14).then(setByDay).catch(console.error);
  }, []);

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Dashboard</h1>
        <p className="text-slate-400 text-sm mt-1">Live traffic enforcement overview</p>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
        <StatCard title="Today's Violations" value={summary?.today_violations ?? "—"} icon={AlertTriangle} color="bg-red-500" />
        <StatCard title="Total Violations" value={summary?.total_violations ?? "—"} icon={TrendingUp} color="bg-orange-500" />
        <StatCard title="Pending Review" value={summary?.pending_violations ?? "—"} icon={Clock} color="bg-yellow-500" />
        <StatCard title="Total Challans" value={summary?.total_challans ?? "—"} icon={FileText} color="bg-blue-500" />
        <StatCard title="Fines Collected" value={`₹${(summary?.fines_collected ?? 0).toLocaleString()}`} icon={IndianRupee} color="bg-green-500" />
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-slate-800 rounded-xl p-5 border border-slate-700">
          <h3 className="text-white font-semibold mb-4">Violations — Last 14 Days</h3>
          {byDay.length === 0 ? (
            <div className="h-48 flex items-center justify-center text-slate-500 text-sm">No data yet</div>
          ) : (
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={byDay}>
                <XAxis dataKey="date" stroke="#475569" tick={{ fontSize: 11 }} />
                <YAxis stroke="#475569" tick={{ fontSize: 11 }} />
                <Tooltip {...tooltip} />
                <Line type="monotone" dataKey="count" stroke="#ef4444" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          )}
        </div>
        <div className="bg-slate-800 rounded-xl p-5 border border-slate-700">
          <h3 className="text-white font-semibold mb-4">Violations by Type</h3>
          {byType.length === 0 ? (
            <div className="h-48 flex items-center justify-center text-slate-500 text-sm">No data yet</div>
          ) : (
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie data={byType} dataKey="count" nameKey="type" cx="50%" cy="50%" outerRadius={70}>
                  {byType.map((_, i) => <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />)}
                </Pie>
                <Tooltip {...tooltip} />
                <Legend wrapperStyle={{ fontSize: 11, color: "#94a3b8" }} />
              </PieChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>
    </div>
  );
}