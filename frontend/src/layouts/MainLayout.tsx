/**
 * MainLayout
 * Authenticated layout with Navbar and main content area.
 */
import { Outlet } from "react-router-dom";
import Navbar from "@/components/layout/Navbar";

const MainLayout = () => (
  <div className="min-h-screen bg-bg-primary">
    <Navbar />
    <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
      <Outlet />
    </main>
  </div>
);

export default MainLayout;
