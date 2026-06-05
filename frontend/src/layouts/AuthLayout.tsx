/**
 * AuthLayout
 * Centered layout for login and register pages with FighterIA logo.
 */
import { Outlet, Link } from "react-router-dom";

const AuthLayout = () => (
  <div className="flex min-h-screen flex-col items-center justify-center bg-bg-primary px-4 py-12">
    <div className="mb-8 text-center">
      <Link to="/" className="inline-flex items-center gap-1">
        <span className="font-display text-4xl font-bold text-brand-red">FIGHTER</span>
        <span className="font-display text-4xl font-bold text-text-primary">IA</span>
      </Link>
      <p className="mt-2 text-sm text-text-secondary">
        Entrena con inteligencia artificial
      </p>
    </div>
    <div className="w-full max-w-md">
      <Outlet />
    </div>
  </div>
);

export default AuthLayout;
