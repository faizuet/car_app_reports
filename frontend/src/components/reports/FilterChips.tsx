import { X } from "lucide-react";
import type { ReportFilters } from "../../types";

const LABELS: Record<string, string> = {
  make: "Make",
  model: "Model",
  year: "Year",
  date_from: "From",
  date_to: "To",
};

interface FilterChipsProps {
  filters: ReportFilters;
  onRemove: (key: keyof ReportFilters) => void;
  onClearAll: () => void;
}

export function FilterChips({ filters, onRemove, onClearAll }: FilterChipsProps) {
  const active = Object.entries(filters).filter(
    ([key, value]) =>
      value &&
      key !== "limit" &&
      key !== "cursor" &&
      String(value).trim() !== ""
  );

  if (active.length === 0) return null;

  return (
    <div className="flex flex-wrap items-center gap-2">
      <span className="text-xs font-medium text-surface-800/50">Active filters:</span>
      {active.map(([key, value]) => (
        <span
          key={key}
          className="inline-flex items-center gap-1.5 rounded-full bg-brand-50 px-3 py-1 text-xs font-medium text-brand-700"
        >
          {LABELS[key] || key}: {String(value)}
          <button
            onClick={() => onRemove(key as keyof ReportFilters)}
            className="rounded-full p-0.5 hover:bg-brand-100"
          >
            <X className="h-3 w-3" />
          </button>
        </span>
      ))}
      <button
        onClick={onClearAll}
        className="text-xs font-medium text-surface-800/50 hover:text-brand-600"
      >
        Clear all
      </button>
    </div>
  );
}
