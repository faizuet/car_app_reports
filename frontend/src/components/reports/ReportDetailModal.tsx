import { Calendar, Hash, Tag, Car } from "lucide-react";
import type { CarReport } from "../../types";
import { Modal } from "../ui/Modal";

interface ReportDetailModalProps {
  report: CarReport | null;
  onClose: () => void;
}

export function ReportDetailModal({ report, onClose }: ReportDetailModalProps) {
  if (!report) return null;

  return (
    <Modal open={!!report} onClose={onClose} title="Report details">
      <div className="space-y-5">
        <div className="rounded-xl bg-gradient-to-br from-brand-50 to-indigo-50 p-5">
          <p className="text-xs font-bold uppercase tracking-wider text-brand-600">{report.make}</p>
          <h3 className="font-display text-2xl font-bold text-surface-900">{report.model}</h3>
          <span className="mt-2 inline-block rounded-full bg-brand-600 px-3 py-1 text-sm font-bold text-white">
            {report.year}
          </span>
        </div>

        <dl className="grid gap-4 sm:grid-cols-2">
          <div className="flex gap-3 rounded-lg border border-surface-200 p-3">
            <Car className="mt-0.5 h-4 w-4 shrink-0 text-surface-800/40" />
            <div>
              <dt className="text-xs font-medium uppercase tracking-wide text-surface-800/50">Make</dt>
              <dd className="font-semibold text-surface-900">{report.make}</dd>
            </div>
          </div>
          <div className="flex gap-3 rounded-lg border border-surface-200 p-3">
            <Car className="mt-0.5 h-4 w-4 shrink-0 text-surface-800/40" />
            <div>
              <dt className="text-xs font-medium uppercase tracking-wide text-surface-800/50">Model</dt>
              <dd className="font-semibold text-surface-900">{report.model}</dd>
            </div>
          </div>
          <div className="flex gap-3 rounded-lg border border-surface-200 p-3">
            <Calendar className="mt-0.5 h-4 w-4 shrink-0 text-surface-800/40" />
            <div>
              <dt className="text-xs font-medium uppercase tracking-wide text-surface-800/50">Year</dt>
              <dd className="font-semibold text-surface-900">{report.year}</dd>
            </div>
          </div>
          <div className="flex gap-3 rounded-lg border border-surface-200 p-3">
            <Tag className="mt-0.5 h-4 w-4 shrink-0 text-surface-800/40" />
            <div>
              <dt className="text-xs font-medium uppercase tracking-wide text-surface-800/50">Category</dt>
              <dd className="font-semibold text-surface-900">{report.category || "—"}</dd>
            </div>
          </div>
          <div className="flex gap-3 rounded-lg border border-surface-200 p-3 sm:col-span-2">
            <Hash className="mt-0.5 h-4 w-4 shrink-0 text-surface-800/40" />
            <div>
              <dt className="text-xs font-medium uppercase tracking-wide text-surface-800/50">Record ID</dt>
              <dd className="font-semibold text-surface-900">#{report.id}</dd>
            </div>
          </div>
        </dl>

        <div className="rounded-lg bg-surface-50 px-4 py-3 text-sm text-surface-800/70">
          <span className="font-medium text-surface-900">Registered: </span>
          {new Date(report.created_at).toLocaleString("en-US", {
            year: "numeric",
            month: "long",
            day: "numeric",
            hour: "2-digit",
            minute: "2-digit",
          })}
          {report.updated_at && (
            <>
              {" · "}
              <span className="font-medium text-surface-900">Updated: </span>
              {new Date(report.updated_at).toLocaleString("en-US", {
                year: "numeric",
                month: "short",
                day: "numeric",
              })}
            </>
          )}
        </div>
      </div>
    </Modal>
  );
}
