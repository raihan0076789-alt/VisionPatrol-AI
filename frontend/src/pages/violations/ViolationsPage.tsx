import { useEffect, useState } from "react";
import { CheckCircle, XCircle, RefreshCw } from "lucide-react";
import { violationsApi } from "../../api/violations";
import { challansApi } from "../../api/challans";
import { Violation } from "../../types";
import Badge from "../../components/shared/Badge";

export default function ViolationsPage() {
  const [violations, setViolations] = useState<Violation[]>([]);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try { setViolations(await violationsApi.list()); }
    finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const confirm = async (id: string) => { await violationsApi.update(id, { status: "confirmed" }); load(); };
  const dismiss = async (id: string) => { await violationsApi.update(id, { status: "dismissed" }); load(); };
  const generateChallan = async (id: string) => {
    try { await challansApi.generate(id); alert("Challan generated!"); load(); }
    catch (e: any) { alert(e.response?.data?.detail || "Error"); }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Violations</h1>
          <p className="text-slate-400 text-sm mt-1">{violations.length} total records</p>
        </div>
        <button onClick={load} className="flex items-center gap-2 text-sm text-slate-400 hover:text-white">
          <RefreshCw size={16} /> Refresh
        </button>
      </div>
      <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-700 text-slate-400">
                <th className="text-left px-4 py-3">Type</th>
                <th className="text-left px-4 py-3">Plate</th>
                <th className="text-left px-4 py-3">Confidence</th>
                <th className="text-left px-4 py-3">Status</th>
                <th className="text-left px-4 py-3">Detected At</th>
                <th className="text-left px-4 py-3">Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={6} className="text-center py-12 text-slate-500">Loading...</td></tr>
              ) : violations.length === 0 ? (
                <tr><td colSpan={6} className="text-center py-12 text-slate-500">No violations found</td></tr>
              ) : violations.map((v) => (
                <tr key={v.id} className="border-b border-slate-700/50 hover:bg-slate-700/30">
                  <td className="px-4 py-3"><Badge value={v.violation_type} /></td>
                  <td className="px-4 py-3 text-white font-mono">{v.plate_number || "—"}</td>
                  <td className="px-4 py-3 text-slate-300">{(v.confidence_score * 100).toFixed(1)}%</td>
                  <td className="px-4 py-3"><Badge value={v.status} /></td>
                  <td className="px-4 py-3 text-slate-400">{new Date(v.detected_at).toLocaleString()}</td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      {v.status === "pending" && (<>
                        <button onClick={() => confirm(v.id)} className="p-1.5 bg-green-500/20 text-green-400 rounded hover:bg-green-500/40" title="Confirm"><CheckCircle size={14} /></button>
                        <button onClick={() => dismiss(v.id)} className="p-1.5 bg-red-500/20 text-red-400 rounded hover:bg-red-500/40" title="Dismiss"><XCircle size={14} /></button>
                      </>)}
                      {v.status === "confirmed" && (
                        <button onClick={() => generateChallan(v.id)} className="px-2 py-1 bg-blue-500/20 text-blue-400 rounded text-xs hover:bg-blue-500/40">Issue Challan</button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}