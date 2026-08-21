import { NavLink, Outlet, Navigate, useLocation } from "react-router-dom";
import {
  Car,
  FileSearch,
  LayoutDashboard,
  LogOut,
  User,
} from "lucide-react";
import { useAuth } from "../../context/AuthContext";
import { Spinner } from "../ui/Spinner";
import { getAvatarUrl } from "../../api/client";

const navItems = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/reports", label: "Reports", icon: FileSearch },
  { to: "/cars", label: "My Cars", icon: Car },
  { to: "/profile", label: "Profile", icon: User },
];

const pageTitles: Record<string, string> = {
  "/dashboard": "Dashboard",
  "/reports": "Registration Reports",
  "/cars": "My Cars",
  "/profile": "Profile",
};

export function AppLayout() {
  const { user, loading, logout } = useAuth();
  const location = useLocation();
  const pageTitle = pageTitles[location.pathname] ?? "AutoReport";

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center gradient-mesh">
        <Spinner size="lg" />
      </div>
    );
  }

  if (!user) {
    const returnTo = encodeURIComponent(location.pathname + location.search);
    return <Navigate to={`/login?returnTo=${returnTo}`} replace />;
  }

  return (
    <div className="flex min-h-screen bg-surface-50">
      <aside className="fixed inset-y-0 left-0 z-30 hidden w-64 flex-col border-r border-surface-200 bg-surface-950 text-white lg:flex">
        <div className="flex h-16 items-center gap-3 border-b border-white/10 px-6">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-brand-600 shadow-lg shadow-brand-600/30">
            <Car className="h-5 w-5" />
          </div>
          <div>
            <p className="font-display text-sm font-bold tracking-tight">AutoReport</p>
            <p className="text-[11px] text-white/50">Registration Portal</p>
          </div>
        </div>

        <nav className="flex-1 space-y-1 p-4">
          {navItems.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition ${
                  isActive
                    ? "bg-brand-600 text-white shadow-lg shadow-brand-600/30"
                    : "text-white/70 hover:bg-white/10 hover:text-white"
                }`
              }
            >
              <Icon className="h-4 w-4" />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="border-t border-white/10 p-4">
          <div className="mb-3 flex items-center gap-3 rounded-lg bg-white/5 px-3 py-2.5">
            {getAvatarUrl(user.profile_image) ? (
              <img
                src={getAvatarUrl(user.profile_image)!}
                alt={user.display_name || user.username}
                className="h-8 w-8 rounded-full object-cover"
              />
            ) : (
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-brand-600 text-xs font-bold">
                {(user.display_name || user.username).charAt(0).toUpperCase()}
              </div>
            )}
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-medium">{user.display_name || user.username}</p>
              <p className="truncate text-xs text-white/50">{user.email}</p>
            </div>
          </div>
          <button
            onClick={logout}
            className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm text-white/70 transition hover:bg-white/10 hover:text-white"
          >
            <LogOut className="h-4 w-4" />
            Sign out
          </button>
        </div>
      </aside>

      <div className="flex flex-1 flex-col lg:pl-64">
        <header className="sticky top-0 z-20 hidden h-16 items-center justify-between border-b border-surface-200 bg-white/80 px-8 backdrop-blur lg:flex">
          <h2 className="font-display text-lg font-semibold text-surface-900">{pageTitle}</h2>
        </header>

        <header className="sticky top-0 z-20 flex h-14 items-center justify-between border-b border-surface-200 bg-white/80 px-4 backdrop-blur lg:hidden">
          <div className="flex items-center gap-2">
            <Car className="h-5 w-5 text-brand-600" />
            <span className="font-display font-bold">{pageTitle}</span>
          </div>
          <button onClick={logout} className="text-sm font-medium text-surface-800">
            Sign out
          </button>
        </header>

        <nav className="flex gap-1 overflow-x-auto border-b border-surface-200 bg-white px-2 py-2 lg:hidden">
          {navItems.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `flex shrink-0 items-center gap-1.5 rounded-lg px-3 py-2 text-xs font-medium transition ${
                  isActive ? "bg-brand-600 text-white" : "text-surface-800"
                }`
              }
            >
              <Icon className="h-3.5 w-3.5" />
              {label}
            </NavLink>
          ))}
        </nav>

        <main className="gradient-mesh flex-1 p-4 md:p-6 lg:p-8">
          <div className="animate-fade-in mx-auto max-w-7xl">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}
