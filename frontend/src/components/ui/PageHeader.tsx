interface PageHeaderProps {
  title: string;
  description?: string;
  action?: React.ReactNode;
}

export function PageHeader({ title, description, action }: PageHeaderProps) {
  return (
    <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
      <div>
        <h1 className="font-display text-2xl font-bold tracking-tight text-surface-900 md:text-3xl">
          {title}
        </h1>
        {description && (
          <p className="mt-1.5 text-sm text-surface-800/60 md:text-base">{description}</p>
        )}
      </div>
      {action && <div className="shrink-0">{action}</div>}
    </div>
  );
}
