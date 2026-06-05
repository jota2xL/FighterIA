/**
 * Navbar
 * Top navigation bar with user dropdown, belt indicator and mobile hamburger menu.
 */
import React from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { useAuthStore } from "@/store/auth.store";
import { getBeltLabel } from "@/utils/format";
import { cn } from "@/utils/cn";

const BELT_COLORS: Record<string, string> = {
  blanco: "bg-belt-blanco",
  amarillo: "bg-belt-amarillo",
  naranja: "bg-belt-naranja",
  verde: "bg-belt-verde",
  azul: "bg-belt-azul",
  marron: "bg-belt-marron",
  negro: "bg-belt-negro border border-border-strong",
};

const NAV_LINKS = [
  { to: "/dashboard", label: "Dashboard" },
  { to: "/analysis/new", label: "Nuevo Análisis" },
  { to: "/history", label: "Historial" },
  { to: "/badges", label: "Logros" },
  { to: "/gyms", label: "Gimnasios" },
];

const Navbar = () => {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();
  const location = useLocation();
  const [dropdownOpen, setDropdownOpen] = React.useState(false);
  const [mobileOpen, setMobileOpen] = React.useState(false);
  const dropdownRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setDropdownOpen(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  React.useEffect(() => {
    setMobileOpen(false);
  }, [location.pathname]);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const isActive = (path: string) => location.pathname === path;

  return (
    <nav className="sticky top-0 z-40 border-b border-border bg-bg-secondary/95 backdrop-blur-sm">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          {/* Logo */}
          <Link to="/dashboard" className="flex items-center gap-2">
            <span className="font-display text-2xl font-bold text-brand-red">FIGHTER</span>
            <span className="font-display text-2xl font-bold text-text-primary">IA</span>
          </Link>

          {/* Desktop nav */}
          <div className="hidden items-center gap-1 md:flex">
            {NAV_LINKS.map((link) => (
              <Link
                key={link.to}
                to={link.to}
                className={cn(
                  "rounded-md px-3 py-2 text-sm font-medium transition-colors",
                  isActive(link.to)
                    ? "bg-bg-hover text-text-primary"
                    : "text-text-secondary hover:text-text-primary hover:bg-bg-hover"
                )}
              >
                {link.label}
              </Link>
            ))}
            {user?.account_type === "instructor" && (
              <Link
                to="/instructor"
                className={cn(
                  "rounded-md px-3 py-2 text-sm font-medium transition-colors",
                  isActive("/instructor")
                    ? "bg-bg-hover text-brand-red"
                    : "text-brand-red hover:bg-bg-hover"
                )}
              >
                Panel Instructor
              </Link>
            )}
          </div>

          {/* User section */}
          <div className="flex items-center gap-3">
            {user && (
              <div className="relative" ref={dropdownRef}>
                <button
                  onClick={() => setDropdownOpen((v) => !v)}
                  className="flex items-center gap-2 rounded-md p-1 hover:bg-bg-hover transition-colors"
                  aria-label="Menú de usuario"
                >
                  {/* Belt indicator */}
                  <span
                    className={cn(
                      "h-3 w-3 rounded-full",
                      BELT_COLORS[user.belt_level] ?? "bg-text-muted"
                    )}
                    title={`Cinturón ${getBeltLabel(user.belt_level)}`}
                  />
                  {/* Avatar */}
                  {user.avatar_url ? (
                    <img
                      src={user.avatar_url}
                      alt={user.username}
                      className="h-8 w-8 rounded-full object-cover border border-border"
                    />
                  ) : (
                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-brand-red text-sm font-bold text-white">
                      {user.username[0].toUpperCase()}
                    </div>
                  )}
                  <span className="hidden text-sm font-medium text-text-primary sm:block">
                    {user.username}
                  </span>
                </button>

                {dropdownOpen && (
                  <div className="absolute right-0 mt-2 w-48 rounded-lg border border-border bg-bg-secondary shadow-xl">
                    <div className="border-b border-border px-4 py-3">
                      <p className="text-sm font-medium text-text-primary">{user.full_name}</p>
                      <p className="text-xs text-text-muted">{user.email}</p>
                    </div>
                    <div className="py-1">
                      <Link
                        to="/profile"
                        onClick={() => setDropdownOpen(false)}
                        className="flex items-center px-4 py-2 text-sm text-text-secondary hover:bg-bg-hover hover:text-text-primary"
                      >
                        Ver perfil
                      </Link>
                      <Link
                        to="/badges"
                        onClick={() => setDropdownOpen(false)}
                        className="flex items-center px-4 py-2 text-sm text-text-secondary hover:bg-bg-hover hover:text-text-primary"
                      >
                        Badges
                      </Link>
                    </div>
                    <div className="border-t border-border py-1">
                      <button
                        onClick={handleLogout}
                        className="flex w-full items-center px-4 py-2 text-sm text-brand-red hover:bg-bg-hover"
                      >
                        Cerrar sesión
                      </button>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Mobile hamburger */}
            <button
              onClick={() => setMobileOpen((v) => !v)}
              className="rounded-md p-2 text-text-secondary hover:bg-bg-hover hover:text-text-primary md:hidden"
              aria-label="Abrir menú"
            >
              {mobileOpen ? (
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              ) : (
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              )}
            </button>
          </div>
        </div>

        {/* Mobile menu */}
        {mobileOpen && (
          <div className="border-t border-border pb-3 pt-2 md:hidden">
            {NAV_LINKS.map((link) => (
              <Link
                key={link.to}
                to={link.to}
                className={cn(
                  "block rounded-md px-3 py-2 text-sm font-medium transition-colors",
                  isActive(link.to)
                    ? "bg-bg-hover text-text-primary"
                    : "text-text-secondary hover:bg-bg-hover hover:text-text-primary"
                )}
              >
                {link.label}
              </Link>
            ))}
            {user?.account_type === "instructor" && (
              <Link
                to="/instructor"
                className="block rounded-md px-3 py-2 text-sm font-medium text-brand-red hover:bg-bg-hover"
              >
                Panel Instructor
              </Link>
            )}
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
