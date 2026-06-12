import { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LineChart, Line } from "recharts";
import { analyticsApi } from "../../api/analytics";

const tooltip = { contentStyle: { backgroundColor: "#1e293b", border: "none", borderRadius: 8 }, labelStyle: { color: "#94a3b8" } };

export default function AnalyticsPage() {
  const [byType, setByType] = useState<{ type: string; count: number }[]>([]);
  const [byDay, setByDay] = useState<{ date: string; count: number }[]>([]);
  const [topOffenders, setTopOffenders] = useState<{ plate: string; count: number }[]>([]);

  useEffect(() => {
    analyticsApi.byType(30).then(setByType);
    analyticsApi.byDay(30).then(setByDay);
    analyticsApi.topOffenders().then(setTopOffenders);
  }, []);

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Analytics</h1>
        <p className="text-slate-400 text-sm mt-1">Last 30 days overview</p>
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-slate-800 rounded-xl p-5 border border-slate-700">
          <h3 className="text-white font-semibold mb-4">Violations by Type</h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={byType}>
              <XAxis dataKey="type" stroke="#475569" tick={{ fontSize: 10 }} />
              <YAxis stroke="#475569" tick={{ fontSize: 10 }} />
              <Tooltip {...tooltip} />
              <Bar dataKey="count" fill="#ef4444" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="bg-slate-800 rounded-xl p-5 border border-slate-700">
          <h3 className="text-white font-semibold mb-4">Daily Trend</h3>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={byDay}>
              <XAxis dataKey="date" stroke="#475569" tick={{ fontSize: 10 }} />
              <YAxis stroke="#475569" tick={{ fontSize: 10 }} />
              <Tooltip {...tooltip} />
              <Line type="monotone" dataKey="count" stroke="#f97316" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div className="bg-slate-800 rounded-xl p-5 border border-slate-700 lg:col-span-2">
          <h3 className="text-white font-semibold mb-4">Top Offending Vehicles</h3>
          {topOffenders.length === 0 ? (
            <p className="text-slate-500 text-sm text-center py-8">No data yet</p>
          ) : (
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={topOffenders} layout="vertical">
                <XAxis type="number" stroke="#475569" tick={{ fontSize: 10 }} />
                <YAxis dataKey="plate" type="category" stroke="#475569" tick={{ fontSize: 10 }} width={100} />
                <Tooltip {...tooltip} />
                <Bar dataKey="count" fill="#a855f7" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>
    </div>
  );
}