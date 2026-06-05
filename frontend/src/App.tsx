import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import MainLayout from "@/layouts/MainLayout";
import AuthLayout from "@/layouts/AuthLayout";
import { useAuthStore } from "@/store/auth.store";

import LandingPage from "@/pages/LandingPage";
import LoginPage from "@/pages/LoginPage";
import RegisterPage from "@/pages/RegisterPage";
import DashboardPage from "@/pages/DashboardPage";
import NewAnalysisPage from "@/pages/NewAnalysisPage";
import AnalysisResultPage from "@/pages/AnalysisResultPage";
import HistoryPage from "@/pages/HistoryPage";
import ProfilePage from "@/pages/ProfilePage";
import BadgesPage from "@/pages/BadgesPage";
import InstructorPanelPage from "@/pages/InstructorPanelPage";
import InstructorGroupPage from "@/pages/InstructorGroupPage";
import InstructorStudentPage from "@/pages/InstructorStudentPage";
import NotFoundPage from "@/pages/NotFoundPage";
import GymManagementPage from "@/pages/GymManagementPage";
import LeadPipelinePage from "@/pages/LeadPipelinePage";
import BusinessDashboardPage from "@/pages/BusinessDashboardPage";
import CertificatePage from "@/pages/CertificatePage";

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated());
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />;
};

const InstructorRoute = ({ children }: { children: React.ReactNode }) => {
  const user = useAuthStore((s) => s.user);
  if (!user) return <Navigate to="/login" replace />;
  if (user.account_type !== "instructor") return <Navigate to="/dashboard" replace />;
  return <>{children}</>;
};

const App = () => (
  <BrowserRouter>
    <Routes>
      {/* Public */}
      <Route path="/" element={<LandingPage />} />
      <Route element={<AuthLayout />}>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
      </Route>

      {/* Protected */}
      <Route
        element={
          <ProtectedRoute>
            <MainLayout />
          </ProtectedRoute>
        }
      >
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/analysis/new" element={<NewAnalysisPage />} />
        <Route path="/analysis/:id" element={<AnalysisResultPage />} />
        <Route path="/history" element={<HistoryPage />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/badges" element={<BadgesPage />} />
        <Route path="/instructor" element={<InstructorPanelPage />} />
        <Route path="/gyms" element={<GymManagementPage />} />
        <Route path="/gyms/:gymId/leads" element={<LeadPipelinePage />} />
        <Route path="/gyms/:gymId/dashboard" element={<BusinessDashboardPage />} />
        <Route path="/certificates/:hash" element={<CertificatePage />} />
      </Route>

      {/* Instructor-only */}
      <Route
        element={
          <ProtectedRoute>
            <InstructorRoute>
              <MainLayout />
            </InstructorRoute>
          </ProtectedRoute>
        }
      >
        <Route
          path="/instructor/groups/:groupId"
          element={<InstructorGroupPage />}
        />
        <Route
          path="/instructor/students/:studentId"
          element={<InstructorStudentPage />}
        />
      </Route>

      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  </BrowserRouter>
);

export default App;
