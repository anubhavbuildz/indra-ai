import { LoaderCircle } from "lucide-react";
import { cn } from "../../lib/utils";

export function Button({ className, variant = "primary", size = "md", children, ...props }) {
  return (
    <button
      className={cn("button", `button-${variant}`, `button-${size}`, className)}
      {...props}
    >
      {children}
    </button>
  );
}

export function Card({ className, children, ...props }) {
  return (
    <section className={cn("card", className)} {...props}>
      {children}
    </section>
  );
}

export function Badge({ className, tone = "neutral", children }) {
  return <span className={cn("badge", `badge-${tone}`, className)}>{children}</span>;
}

export function Input({ className, ...props }) {
  return <input className={cn("input", className)} {...props} />;
}

export function PageHeading({ eyebrow, title, description, action }) {
  return (
    <div className="page-heading">
      <div>
        {eyebrow && <div className="eyebrow">{eyebrow}</div>}
        <h1>{title}</h1>
        {description && <p>{description}</p>}
      </div>
      {action && <div className="page-heading-action">{action}</div>}
    </div>
  );
}

export function LoadingState({ label = "Loading data…" }) {
  return (
    <div className="loading-state">
      <LoaderCircle className="spin" size={17} />
      <span>{label}</span>
    </div>
  );
}

export function ErrorState({ error, onRetry }) {
  return (
    <div className="error-state" role="alert">
      <strong>Couldn’t load this data</strong>
      <span>{error?.message || "The backend request failed."}</span>
      {onRetry && (
        <Button size="sm" variant="outline" onClick={onRetry}>
          Try again
        </Button>
      )}
    </div>
  );
}

export function EmptyState({ icon: Icon, title, description, action }) {
  return (
    <div className="empty-state">
      {Icon && (
        <div className="empty-icon">
          <Icon size={20} />
        </div>
      )}
      <strong>{title}</strong>
      <p>{description}</p>
      {action}
    </div>
  );
}
