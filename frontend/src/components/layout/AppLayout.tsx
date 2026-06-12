import { Navigate, Outlet } from "react-router-dom";
import Sidebar from "./Sidebar";
import { useAuthStore } from "../../store/authStore";

export default function AppLayout() {
  const { isAuthenticated } = useAuthStore();
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return (
    <div className="flex min-h-screen bg-slate-950">
      <Sidebar />
      <main className="flex-1 overflow-auto">
        <Outlet />
      </main>
    </div>
  );
}