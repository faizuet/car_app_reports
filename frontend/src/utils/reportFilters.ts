import type { ReportFilters } from "../types";

export const emptyReportFilters: ReportFilters = {
  make: "",
  model: "",
  year: "",
  date_from: "",
  date_to: "",
  limit: 12,
};

export function filtersFromSearchParams(params: URLSearchParams): ReportFilters {
  const limitParam = params.get("limit");
  return {
    make: params.get("make") ?? "",
    model: params.get("model") ?? "",
    year: params.get("year") ?? "",
    date_from: params.get("date_from") ?? "",
    date_to: params.get("date_to") ?? "",
    limit: limitParam ? Number(limitParam) : 12,
  };
}

export function searchParamsFromFilters(filters: ReportFilters): URLSearchParams {
  const params = new URLSearchParams();
  if (filters.make) params.set("make", filters.make);
  if (filters.model) params.set("model", filters.model);
  if (filters.year) params.set("year", filters.year);
  if (filters.date_from) params.set("date_from", filters.date_from);
  if (filters.date_to) params.set("date_to", filters.date_to);
  if (filters.limit && filters.limit !== 12) params.set("limit", String(filters.limit));
  return params;
}

export function matchesQuickFilter(
  applied: ReportFilters,
  preset: Partial<ReportFilters>
): boolean {
  const expected = { ...emptyReportFilters, ...preset };
  return (
    applied.make === expected.make &&
    applied.model === expected.model &&
    applied.year === expected.year &&
    applied.date_from === expected.date_from &&
    applied.date_to === expected.date_to
  );
}
