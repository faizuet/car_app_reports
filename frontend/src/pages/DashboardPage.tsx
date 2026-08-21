import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { FileSearch, Car, Database, Layers, ArrowRight, AlertCircle, RotateCcw } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { searchReports } from "../api/reports";
import { listCars } from "../api/cars";
import { PageHeader } from "../components/ui/PageHeader";
import { StatCardSkeleton } from "../components/ui/Skeleton";

export function DashboardPage() {
  const { user } = useAuth();
  const [totalReports, setTotalReports] = useState<number | null>(null);
  const [myCars, setMyCars] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadStats = async () => {
    setLoading(true);
    setError(null);
    try {
      const [reports, cars] = await Promise.all([
        searchReports({ limit: 1 }),
        listCars(1),
      ]);
      setTotalReports(reports.total);
      setMyCars(cars.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load dashboard stats");
      setTotalReports(null);
      setMyCars(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStats();
  }, []);

  const stats = [
    {
      label: "Total Reports",
      value: totalReports?.toLocaleString() ?? "—",
      icon: Database,
      bg: "bg-blue-50 text-blue-600",
    },
    {
      label: "My Cars",
      value: myCars?.toString() ?? "—",
      icon: Car,
      bg: "bg-emerald-50 text-emerald-600",
    },
    {
      label: "Dataset Range",
      value: "2012–2022",
      icon: Layers,
      bg: "bg-violet-50 text-violet-600",
    },
  ];

  return (
    <div className="space-y-8">
      <PageHeader
        title={`Welcome back, ${user?.display_name || user?.username}`}
        description="Search and explore car registration reports from the synced dataset."
      />

      {error && (
        <div className="flex items-center justify-between gap-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">
          <div className="flex items-center gap-2">
            <AlertCircle className="h-4 w-4 shrink-0" />
            <span>{error}</span>
          </div>
          <button onClick={loadStats} className="btn-secondary shrink-0 py-1.5 text-xs">
            <RotateCcw className="h-3.5 w-3.5" /> Retry
          </button>
        </div>
      )}

      <div className="grid gap-4 sm:grid-cols-3">
        {loading
          ? Array.from({ length: 3 }).map((_, i) => <StatCardSkeleton key={i} />)
          : stats.map(({ label, value, icon: Icon, bg }) => (
              <div key={label} className="card relative overflow-hidden p-5">
                <div className={`mb-3 inline-flex rounded-xl p-2.5 ${bg}`}>
                  <Icon className="h-5 w-5" />
                </div>
                <p className="text-3xl font-bold tracking-tight text-surface-900">{value}</p>
                <p className="text-sm text-surface-800/60">{label}</p>
              </div>
            ))}
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Link
          to="/reports"
          className="group card relative overflow-hidden p-6 transition hover:border-brand-300 hover:shadow-elevated"
        >
          <div className="absolute right-0 top-0 h-32 w-32 translate-x-8 -translate-y-8 rounded-full bg-brand-50 transition group-hover:bg-brand-100" />
          <div className="relative">
            <div className="mb-4 inline-flex rounded-xl bg-brand-600 p-3 text-white shadow-lg shadow-brand-600/30 transition group-hover:scale-105">
              <FileSearch className="h-6 w-6" />
            </div>
            <h2 className="font-display text-xl font-bold">Search Reports</h2>
            <p className="mt-2 text-sm text-surface-800/60">
              Filter by make, model, year, and registration date with instant results.
            </p>
            <span className="mt-5 inline-flex items-center gap-1 text-sm font-semibold text-brand-600">
              Open reports <ArrowRight className="h-4 w-4 transition group-hover:translate-x-1" />
            </span>
          </div>
        </Link>

        <Link
          to="/cars"
          className="group card relative overflow-hidden p-6 transition hover:border-brand-300 hover:shadow-elevated"
        >
          <div className="absolute right-0 top-0 h-32 w-32 translate-x-8 -translate-y-8 rounded-full bg-surface-100 transition group-hover:bg-surface-200" />
          <div className="relative">
            <div className="mb-4 inline-flex rounded-xl bg-surface-900 p-3 text-white shadow-lg transition group-hover:scale-105">
              <Car className="h-6 w-6" />
            </div>
            <h2 className="font-display text-xl font-bold">My Cars</h2>
            <p className="mt-2 text-sm text-surface-800/60">
              Register and manage vehicles linked to your account.
            </p>
            <span className="mt-5 inline-flex items-center gap-1 text-sm font-semibold text-brand-600">
              View my cars <ArrowRight className="h-4 w-4 transition group-hover:translate-x-1" />
            </span>
          </div>
        </Link>
      </div>

      <div className="card p-6">
        <h3 className="font-display font-bold text-surface-900">How it works</h3>
        <div className="mt-5 grid gap-4 sm:grid-cols-3">
          {[
            { step: "1", title: "Set filters", desc: "Choose make, model, year, or date range" },
            { step: "2", title: "Search", desc: "Browse paginated registration reports" },
            { step: "3", title: "Manage cars", desc: "Register and track your own vehicles" },
          ].map(({ step, title, desc }) => (
            <div key={step} className="flex gap-3">
              <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-brand-600 text-sm font-bold text-white">
                {step}
              </span>
              <div>
                <p className="font-semibold text-surface-900">{title}</p>
                <p className="text-sm text-surface-800/60">{desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
