import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import "./index.css";
import AppLayout from "./components/layout/AppLayout";
import LoginPage from "./pages/auth/LoginPage";
import DashboardPage from "./pages/dashboard/DashboardPage";
import ViolationsPage from "./pages/violations/ViolationsPage";
import ChallansPage from "./pages/challans/ChallansPage";
import AnalyticsPage from "./pages/analytics/AnalyticsPage";
import VehiclesPage from "./pages/vehicles/VehiclesPage";

const queryClient = new QueryClient();

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/" element={<AppLayout />}>
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<DashboardPage />} />
            <Route path="violations" element={<ViolationsPage />} />
            <Route path="challans" element={<ChallansPage />} />
            <Route path="analytics" element={<AnalyticsPage />} />
            <Route path="vehicles" element={<VehiclesPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  </StrictMode>
);