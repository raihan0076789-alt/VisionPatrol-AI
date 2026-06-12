import { useState, useRef } from "react";
import { Upload, CheckCircle, Clock, XCircle, Film } from "lucide-react";
import { uploadApi } from "../../api/upload";

type SessionResult = {
  session_id: string;
  status: string;
  violations_found?: number;
  filename?: string;
};

export default function UploadPage() {
  const [dragging, setDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState<SessionResult | null>(null);
  const [error, setError] = useState("");
  const [sessions, setSessions] = useState<SessionResult[]>([]);
  const fileRef = useRef<HTMLInputElement>(null);

  const handleFile = async (file: File) => {
    setError("");
    setResult(null);
    setUploading(true);
    setProgress(0);

    try {
      const res = await uploadApi.uploadVideo(file, setProgress);
      setResult({ ...res, filename: file.name });

      // Poll for completion
      const poll = setInterval(async () => {
        const status = await uploadApi.getSessionStatus(res.session_id);
        if (status.status === "completed" || status.status === "failed") {
          clearInterval(poll);
          setResult((prev) => prev ? { ...prev, ...status } : status);
          loadSessions();
        }
      }, 2000);

    } catch (e: any) {
      setError(e.response?.data?.detail || "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  const loadSessions = async () => {
    try {
      const data = await uploadApi.getSessions();
      setSessions(data);
    } catch {}
  };

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  };

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Upload Video</h1>
        <p className="text-slate-400 text-sm mt-1">Upload traffic footage for AI violation detection</p>
      </div>

      {/* Drop Zone */}
      <div
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        onClick={() => fileRef.current?.click()}
        className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-all ${
          dragging ? "border-red-500 bg-red-500/10" : "border-slate-600 hover:border-slate-400"
        }`}
      >
        <input
          ref={fileRef}
          type="file"
          accept=".mp4,.avi,.mov,.mkv"
          className="hidden"
          onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
        />
        <Upload size={40} className="text-slate-500 mx-auto mb-4" />
        <p className="text-white font-medium">Drop video here or click to browse</p>
        <p className="text-slate-500 text-sm mt-1">MP4, AVI, MOV, MKV — Max 500MB</p>
      </div>

      {/* Upload Progress */}
      {uploading && (
        <div className="bg-slate-800 rounded-xl p-5 border border-slate-700">
          <div className="flex items-center justify-between mb-2">
            <p className="text-white text-sm font-medium">Uploading...</p>
            <p className="text-slate-400 text-sm">{progress}%</p>
          </div>
          <div className="w-full bg-slate-700 rounded-full h-2">
            <div
              className="bg-red-500 h-2 rounded-full transition-all"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="bg-red-500/10 border border-red-500/30 text-red-400 px-4 py-3 rounded-lg text-sm">
          {error}
        </div>
      )}

      {/* Result */}
      {result && (
        <div className="bg-slate-800 rounded-xl p-5 border border-slate-700">
          <div className="flex items-center gap-3">
            {result.status === "completed" ? (
              <CheckCircle size={24} className="text-green-400" />
            ) : result.status === "failed" ? (
              <XCircle size={24} className="text-red-400" />
            ) : (
              <Clock size={24} className="text-yellow-400 animate-spin" />
            )}
            <div>
              <p className="text-white font-medium">{result.filename}</p>
              <p className="text-slate-400 text-sm">
                Status: <span className="capitalize">{result.status}</span>
                {result.violations_found !== undefined && result.violations_found > 0 &&
                  ` — ${result.violations_found} violations detected`}
              </p>
            </div>
          </div>
          {result.status === "completed" && result.violations_found && result.violations_found > 0 && (
            <div className="mt-4 p-3 bg-green-500/10 border border-green-500/30 rounded-lg">
              <p className="text-green-400 text-sm">
                ✅ {result.violations_found} violations found. Go to Violations page to review and issue challans.
              </p>
            </div>
          )}
        </div>
      )}

      {/* Recent Sessions */}
      <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
        <div className="flex items-center justify-between px-5 py-4 border-b border-slate-700">
          <h3 className="text-white font-semibold">Recent Sessions</h3>
          <button onClick={loadSessions} className="text-xs text-slate-400 hover:text-white">
            Refresh
          </button>
        </div>
        {sessions.length === 0 ? (
          <div className="p-8 text-center text-slate-500 text-sm">
            <Film size={32} className="mx-auto mb-2 opacity-30" />
            No sessions yet — upload a video to start
          </div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-slate-400 border-b border-slate-700">
                <th className="text-left px-5 py-3">Filename</th>
                <th className="text-left px-5 py-3">Status</th>
                <th className="text-left px-5 py-3">Violations</th>
                <th className="text-left px-5 py-3">Started</th>
              </tr>
            </thead>
            <tbody>
              {sessions.map((s: any) => (
                <tr key={s.id} className="border-b border-slate-700/50 hover:bg-slate-700/30">
                  <td className="px-5 py-3 text-white">{s.filename}</td>
                  <td className="px-5 py-3">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      s.status === "completed" ? "bg-green-500/20 text-green-400" :
                      s.status === "failed" ? "bg-red-500/20 text-red-400" :
                      "bg-yellow-500/20 text-yellow-400"
                    }`}>{s.status}</span>
                  </td>
                  <td className="px-5 py-3 text-slate-300">{s.violations_found || 0}</td>
                  <td className="px-5 py-3 text-slate-400">
                    {new Date(s.started_at).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}