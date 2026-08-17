import { apiRequest, buildQuery } from "./client";
import type { CarReport, CursorPage, ReportFilters } from "../types";

export async function searchReports(
  filters: ReportFilters
): Promise<CursorPage<CarReport>> {
  return apiRequest<CursorPage<CarReport>>(
    `/reports/${buildQuery({
      make: filters.make,
      model: filters.model,
      year: filters.year ? Number(filters.year) : undefined,
      date_from: filters.date_from,
      date_to: filters.date_to,
      limit: filters.limit ?? 12,
      cursor: filters.cursor,
    })}`
  );
}
