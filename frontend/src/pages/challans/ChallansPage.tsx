import { useEffect, useState } from "react";
import { Download, RefreshCw } from "lucide-react";
import { challansApi } from "../../api/challans";
import { Challan } from "../../types";
import Badge from "../../components/shared/Badge";

export default function ChallansPage() {
  const [challans, setChallans] = useState<Challan[]>([]);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try { setChallans(await challansApi.list()); }
    finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Challans</h1>
          <p className="text-slate-400 text-sm mt-1">{challans.length} total challans</p>
        </div>
        <button onClick={load} className="flex items-center gap-2 text-sm text-slate-400 hover:text-white">
          <RefreshCw size={16} /> Refresh
        </button>
      </div>
      <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-700 text-slate-400">
              <th className="text-left px-4 py-3">Challan No.</th>
              <th className="text-left px-4 py-3">Fine Amount</th>
              <th className="text-left px-4 py-3">Status</th>
              <th className="text-left px-4 py-3">Due Date</th>
              <th className="text-left px-4 py-3">Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={5} className="text-center py-12 text-slate-500">Loading...</td></tr>
            ) : challans.length === 0 ? (
              <tr><td colSpan={5} className="text-center py-12 text-slate-500">No challans yet</td></tr>
            ) : challans.map((c) => (
              <tr key={c.id} className="border-b border-slate-700/50 hover:bg-slate-700/30">
                <td className="px-4 py-3 text-white font-mono">{c.challan_number}</td>
                <td className="px-4 py-3 text-green-400 font-medium">₹{c.fine_amount.toLocaleString()}</td>
                <td className="px-4 py-3"><Badge value={c.status} /></td>
                <td className="px-4 py-3 text-slate-400">{c.due_date ? new Date(c.due_date).toLocaleDateString() : "—"}</td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    {c.pdf_path && (
                      <a href={challansApi.downloadUrl(c.id)} target="_blank"
                        className="p-1.5 bg-slate-700 text-slate-300 rounded hover:bg-slate-600" title="Download PDF">
                        <Download size={14} />
                      </a>
                    )}
                    {c.status === "generated" && (
                      <button onClick={() => challansApi.update(c.id, "served").then(load)}
                        className="px-2 py-1 bg-purple-500/20 text-purple-400 rounded text-xs hover:bg-purple-500/40">Mark Served</button>
                    )}
                    {c.status === "served" && (
                      <button onClick={() => challansApi.update(c.id, "paid").then(load)}
                        className="px-2 py-1 bg-green-500/20 text-green-400 rounded text-xs hover:bg-green-500/40">Mark Paid</button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}