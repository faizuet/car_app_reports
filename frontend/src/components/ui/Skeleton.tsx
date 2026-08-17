export function Skeleton({ className = "" }: { className?: string }) {
  return (
    <div className={`animate-pulse rounded-lg bg-surface-200/80 ${className}`} />
  );
}

export function ReportCardSkeleton() {
  return (
    <div className="card p-5">
      <div className="mb-3 flex justify-between">
        <div className="space-y-2">
          <Skeleton className="h-3 w-16" />
          <Skeleton className="h-6 w-32" />
        </div>
        <Skeleton className="h-6 w-12 rounded-full" />
      </div>
      <Skeleton className="mb-3 h-4 w-24" />
      <Skeleton className="h-3 w-28" />
    </div>
  );
}

export function StatCardSkeleton() {
  return (
    <div className="card p-5">
      <Skeleton className="mb-3 h-10 w-10 rounded-lg" />
      <Skeleton className="mb-2 h-8 w-20" />
      <Skeleton className="h-4 w-24" />
    </div>
  );
}
