/**
 * Input
 * Form input with label, error and hint support.
 */
import React from "react";
import { cn } from "@/utils/cn";

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  hint?: string;
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, hint, className, id, ...props }, ref) => {
    const inputId = id ?? label?.toLowerCase().replace(/\s+/g, "-");

    return (
      <div className="flex flex-col gap-1">
        {label && (
          <label
            htmlFor={inputId}
            className="text-sm font-medium text-text-secondary"
          >
            {label}
          </label>
        )}
        <input
          ref={ref}
          id={inputId}
          className={cn(
            "rounded-md border bg-bg-tertiary px-3 py-2 text-sm text-text-primary placeholder-text-muted transition-colors",
            "focus:outline-none focus:ring-2 focus:ring-brand-red focus:ring-offset-1 focus:ring-offset-bg-primary",
            error
              ? "border-brand-red-light"
              : "border-border hover:border-border-strong",
            className
          )}
          {...props}
        />
        {error && <p className="text-xs text-brand-red-light">{error}</p>}
        {!error && hint && (
          <p className="text-xs text-text-muted">{hint}</p>
        )}
      </div>
    );
  }
);

Input.displayName = "Input";

export default Input;
