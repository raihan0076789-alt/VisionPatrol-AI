const colors: Record<string, string> = {
  pending: "bg-yellow-500/20 text-yellow-400",
  confirmed: "bg-green-500/20 text-green-400",
  dismissed: "bg-slate-500/20 text-slate-400",
  challan_issued: "bg-blue-500/20 text-blue-400",
  generated: "bg-blue-500/20 text-blue-400",
  served: "bg-purple-500/20 text-purple-400",
  paid: "bg-green-500/20 text-green-400",
  cancelled: "bg-red-500/20 text-red-400",
  helmet: "bg-red-500/20 text-red-400",
  triple_riding: "bg-orange-500/20 text-orange-400",
  signal_jump: "bg-yellow-500/20 text-yellow-400",
  wrong_side: "bg-pink-500/20 text-pink-400",
  no_plate: "bg-purple-500/20 text-purple-400",
  over_speed: "bg-cyan-500/20 text-cyan-400",
};

export default function Badge({ value }: { value: string }) {
  return (
    <span className={`px-2 py-1 rounded-md text-xs font-medium ${colors[value] || "bg-slate-700 text-slate-300"}`}>
      {value.replace(/_/g, " ").toUpperCase()}
    </span>
  );
}