import type { LucideIcon } from "lucide-react";

interface EmptyStateProps {
  icon: LucideIcon;
  title: string;
  description: string;
  action?: React.ReactNode;
}

export function EmptyState({ icon: Icon, title, description, action }: EmptyStateProps) {
  return (
    <div className="card flex flex-col items-center justify-center py-16 text-center">
      <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-surface-100">
        <Icon className="h-8 w-8 text-surface-800/30" />
      </div>
      <h3 className="font-display text-lg font-bold text-surface-900">{title}</h3>
      <p className="mt-1.5 max-w-sm text-sm text-surface-800/60">{description}</p>
      {action && <div className="mt-6">{action}</div>}
    </div>
  );
}
