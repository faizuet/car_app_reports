import type { KeyboardEvent } from "react";
import { Calendar, Tag } from "lucide-react";
import type { CarReport } from "../../types";

const categoryColors: Record<string, string> = {
  SUV: "bg-orange-50 text-orange-700",
  Sedan: "bg-blue-50 text-blue-700",
  Coupe: "bg-purple-50 text-purple-700",
  Pickup: "bg-amber-50 text-amber-700",
  Wagon: "bg-teal-50 text-teal-700",
};

function getCategoryStyle(category: string | null) {
  if (!category) return "bg-surface-100 text-surface-800";
  const key = Object.keys(categoryColors).find((k) =>
    category.toLowerCase().includes(k.toLowerCase())
  );
  return key ? categoryColors[key] : "bg-surface-100 text-surface-800";
}

interface ReportCardProps {
  report: CarReport;
  onSelect?: (report: CarReport) => void;
}

export function ReportCard({ report, onSelect }: ReportCardProps) {
  const handleKeyDown = (e: KeyboardEvent) => {
    if (onSelect && (e.key === "Enter" || e.key === " ")) {
      e.preventDefault();
      onSelect(report);
    }
  };

  return (
    <article
      className={`group card overflow-hidden transition hover:border-brand-200 hover:shadow-elevated ${
        onSelect ? "cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500" : ""
      }`}
      onClick={() => onSelect?.(report)}
      onKeyDown={handleKeyDown}
      tabIndex={onSelect ? 0 : undefined}
      role={onSelect ? "button" : undefined}
      aria-label={onSelect ? `View details for ${report.make} ${report.model} ${report.year}` : undefined}
    >
      <div className="h-1 bg-gradient-to-r from-brand-500 to-brand-600 opacity-0 transition group-hover:opacity-100" />
      <div className="p-5">
        <div className="mb-3 flex items-start justify-between gap-2">
          <div>
            <p className="text-xs font-bold uppercase tracking-wider text-brand-600">
              {report.make}
            </p>
            <h3 className="font-display text-xl font-bold text-surface-900">
              {report.model}
            </h3>
          </div>
          <span className="rounded-full bg-brand-600 px-3 py-1 text-sm font-bold text-white shadow-sm">
            {report.year}
          </span>
        </div>

        {report.category && (
          <span
            className={`mb-3 inline-flex items-center gap-1 rounded-md px-2 py-1 text-xs font-medium ${getCategoryStyle(report.category)}`}
          >
            <Tag className="h-3 w-3" />
            {report.category}
          </span>
        )}

        <div className="flex items-center gap-1.5 border-t border-surface-100 pt-3 text-xs text-surface-800/50">
          <Calendar className="h-3.5 w-3.5" />
          Registered{" "}
          {new Date(report.created_at).toLocaleDateString("en-US", {
            year: "numeric",
            month: "short",
            day: "numeric",
          })}
        </div>
      </div>
    </article>
  );
}
