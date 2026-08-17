import { useCallback, useEffect, useState, type FormEvent } from "react";
import { Search, RotateCcw, ChevronRight, Car, LayoutGrid, List } from "lucide-react";
import { searchReports } from "../api/reports";
import type { CarReport, ReportFilters } from "../types";
import { PageHeader } from "../components/ui/PageHeader";
import { Spinner } from "../components/ui/Spinner";
import { ReportCardSkeleton } from "../components/ui/Skeleton";
import { EmptyState } from "../components/ui/EmptyState";
import { FilterChips } from "../components/reports/FilterChips";
import { ReportCard } from "../components/reports/ReportCard";
import { useToast } from "../context/ToastContext";

const emptyFilters: ReportFilters = {
  make: "",
  model: "",
  year: "",
  date_from: "",
  date_to: "",
  limit: 12,
};

const yearOptions = Array.from({ length: 11 }, (_, i) => 2012 + i);

const QUICK_FILTERS = [
  { label: "Toyota", filters: { make: "Toyota" } },
  { label: "Ford", filters: { make: "Ford" } },
  { label: "Audi", filters: { make: "Audi" } },
  { label: "BMW", filters: { make: "BMW" } },
  { label: "Audi Q3 2020", filters: { make: "Audi", model: "Q3", year: "2020" } },
  { label: "Year 2018", filters: { year: "2018" } },
];

export function ReportsPage() {
  const { toast } = useToast();
  const [filters, setFilters] = useState<ReportFilters>(emptyFilters);
  const [applied, setApplied] = useState<ReportFilters>(emptyFilters);
  const [items, setItems] = useState<CarReport[]>([]);
  const [total, setTotal] = useState(0);
  const [nextCursor, setNextCursor] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid");

  const fetchReports = useCallback(async (f: ReportFilters, append = false) => {
    if (append) setLoadingMore(true);
    else setLoading(true);

    try {
      const data = await searchReports(f);
      setTotal(data.total);
      setNextCursor(data.next_cursor);
      setItems((prev) => (append ? [...prev, ...data.items] : data.items));
    } catch (err) {
      toast(err instanceof Error ? err.message : "Failed to load reports", "error");
      if (!append) setItems([]);
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  }, [toast]);

  useEffect(() => {
    fetchReports(applied);
  }, [applied, fetchReports]);

  const handleSearch = (e: FormEvent) => {
    e.preventDefault();
    setApplied({ ...filters, cursor: undefined });
  };

  const applyQuickFilter = (preset: Partial<ReportFilters>) => {
    const next = { ...emptyFilters, ...preset };
    setFilters(next);
    setApplied({ ...next, cursor: undefined });
  };

  const handleReset = () => {
    setFilters(emptyFilters);
    setApplied(emptyFilters);
  };

  const removeFilter = (key: keyof ReportFilters) => {
    const next = { ...applied, [key]: "", cursor: undefined };
    setFilters(next);
    setApplied(next);
  };

  const loadMore = () => {
    if (!nextCursor) return;
    const next = { ...applied, cursor: nextCursor };
    fetchReports(next, true);
    setApplied(next);
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Registration Reports"
        description="Search synced car data by make, model, year, and date"
      />

      <div className="flex flex-wrap gap-2">
        <span className="self-center text-xs font-medium text-surface-800/50">Quick filters:</span>
        {QUICK_FILTERS.map(({ label, filters: preset }) => (
          <button
            key={label}
            type="button"
            onClick={() => applyQuickFilter(preset)}
            className="chip"
          >
            {label}
          </button>
        ))}
      </div>

      <form onSubmit={handleSearch} className="card p-5 md:p-6">
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
          <div>
            <label className="mb-1.5 block text-xs font-semibold uppercase tracking-wide text-surface-800/50">
              Make
            </label>
            <input
              className="input-field"
              placeholder="e.g. Toyota"
              value={filters.make}
              onChange={(e) => setFilters({ ...filters, make: e.target.value })}
            />
          </div>
          <div>
            <label className="mb-1.5 block text-xs font-semibold uppercase tracking-wide text-surface-800/50">
              Model
            </label>
            <input
              className="input-field"
              placeholder="e.g. Corolla"
              value={filters.model}
              onChange={(e) => setFilters({ ...filters, model: e.target.value })}
            />
          </div>
          <div>
            <label className="mb-1.5 block text-xs font-semibold uppercase tracking-wide text-surface-800/50">
              Year
            </label>
            <select
              className="input-field"
              value={filters.year}
              onChange={(e) => setFilters({ ...filters, year: e.target.value })}
            >
              <option value="">All years</option>
              {yearOptions.map((y) => (
                <option key={y} value={y}>{y}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="mb-1.5 block text-xs font-semibold uppercase tracking-wide text-surface-800/50">
              Date from
            </label>
            <input
              type="datetime-local"
              className="input-field"
              value={filters.date_from}
              onChange={(e) => setFilters({ ...filters, date_from: e.target.value })}
            />
          </div>
          <div>
            <label className="mb-1.5 block text-xs font-semibold uppercase tracking-wide text-surface-800/50">
              Date to
            </label>
            <input
              type="datetime-local"
              className="input-field"
              value={filters.date_to}
              onChange={(e) => setFilters({ ...filters, date_to: e.target.value })}
            />
          </div>
          <div className="flex items-end gap-2 sm:col-span-2 lg:col-span-1">
            <button type="submit" className="btn-primary flex-1">
              <Search className="h-4 w-4" /> Search
            </button>
            <button type="button" onClick={handleReset} className="btn-secondary px-3" title="Reset">
              <RotateCcw className="h-4 w-4" />
            </button>
          </div>
        </div>
      </form>

      <FilterChips filters={applied} onRemove={removeFilter} onClearAll={handleReset} />

      <div className="flex items-center justify-between">
        <p className="text-sm text-surface-800/60">
          {loading ? (
            "Searching..."
          ) : (
            <>
              <span className="font-semibold text-surface-900">{total.toLocaleString()}</span>{" "}
              reports found
              {items.length < total && (
                <span className="text-surface-800/40"> · showing {items.length}</span>
              )}
            </>
          )}
        </p>
        <div className="flex rounded-lg border border-surface-200 bg-white p-0.5">
          <button
            onClick={() => setViewMode("grid")}
            className={`rounded-md p-2 transition ${viewMode === "grid" ? "bg-brand-600 text-white" : "text-surface-800/60 hover:text-surface-900"}`}
          >
            <LayoutGrid className="h-4 w-4" />
          </button>
          <button
            onClick={() => setViewMode("list")}
            className={`rounded-md p-2 transition ${viewMode === "list" ? "bg-brand-600 text-white" : "text-surface-800/60 hover:text-surface-900"}`}
          >
            <List className="h-4 w-4" />
          </button>
        </div>
      </div>

      {loading ? (
        <div className={viewMode === "grid" ? "grid gap-4 sm:grid-cols-2 xl:grid-cols-3" : "space-y-3"}>
          {Array.from({ length: 6 }).map((_, i) => (
            <ReportCardSkeleton key={i} />
          ))}
        </div>
      ) : items.length === 0 ? (
        <EmptyState
          icon={Car}
          title="No reports found"
          description="Try adjusting your filters or use a quick filter above. Run a data sync if the database is empty."
          action={
            <button onClick={handleReset} className="btn-secondary">
              Clear all filters
            </button>
          }
        />
      ) : viewMode === "grid" ? (
        <>
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
            {items.map((report) => (
              <ReportCard key={report.id} report={report} />
            ))}
          </div>
          {nextCursor && (
            <div className="flex justify-center pt-4">
              <button onClick={loadMore} disabled={loadingMore} className="btn-secondary min-w-[140px]">
                {loadingMore ? <Spinner size="sm" /> : (
                  <>Load more <ChevronRight className="h-4 w-4" /></>
                )}
              </button>
            </div>
          )}
        </>
      ) : (
        <>
          <div className="card overflow-hidden">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-surface-200 bg-surface-50">
                <tr>
                  <th className="px-4 py-3 font-semibold">Make</th>
                  <th className="px-4 py-3 font-semibold">Model</th>
                  <th className="px-4 py-3 font-semibold">Year</th>
                  <th className="hidden px-4 py-3 font-semibold md:table-cell">Category</th>
                  <th className="hidden px-4 py-3 font-semibold lg:table-cell">Registered</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-surface-100">
                {items.map((r) => (
                  <tr key={r.id} className="hover:bg-surface-50/50">
                    <td className="px-4 py-3 font-medium text-brand-600">{r.make}</td>
                    <td className="px-4 py-3 font-semibold">{r.model}</td>
                    <td className="px-4 py-3">
                      <span className="rounded-full bg-brand-50 px-2 py-0.5 text-xs font-bold text-brand-700">
                        {r.year}
                      </span>
                    </td>
                    <td className="hidden px-4 py-3 text-surface-800/60 md:table-cell">{r.category || "—"}</td>
                    <td className="hidden px-4 py-3 text-surface-800/50 lg:table-cell">
                      {new Date(r.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {nextCursor && (
            <div className="flex justify-center pt-4">
              <button onClick={loadMore} disabled={loadingMore} className="btn-secondary">
                {loadingMore ? <Spinner size="sm" /> : <>Load more <ChevronRight className="h-4 w-4" /></>}
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
