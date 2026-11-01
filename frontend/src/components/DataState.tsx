type DataStateProps = {
  title: string;
  message?: string;
};

export function EmptyState({ title, message }: DataStateProps) {
  return (
    <div className="py-8 text-center">
      <p className="font-medium text-slate-200">{title}</p>
      {message ? <p className="mt-2 text-sm text-slate-500">{message}</p> : null}
    </div>
  );
}

export function LoadingState({ title }: Pick<DataStateProps, "title">) {
  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900/70 p-8 text-center">
      <p className="text-sm font-medium text-slate-300">{title}</p>
    </div>
  );
}
