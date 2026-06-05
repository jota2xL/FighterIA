/**
 * ErrorMessage
 * Displays an error state with optional retry action.
 */
interface ErrorMessageProps {
  message: string;
  onRetry?: () => void;
}

const ErrorMessage = ({ message, onRetry }: ErrorMessageProps) => (
  <div className="flex flex-col items-center gap-3 rounded-lg border border-brand-red/30 bg-brand-red/5 p-6 text-center">
    <svg
      className="h-8 w-8 text-brand-red"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      aria-hidden="true"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
      />
    </svg>
    <p className="text-sm font-medium text-brand-red-light">{message}</p>
    {onRetry && (
      <button
        onClick={onRetry}
        className="rounded-md bg-brand-red px-4 py-2 text-sm font-semibold text-white hover:bg-brand-red-dark transition-colors"
      >
        Reintentar
      </button>
    )}
  </div>
);

export default ErrorMessage;
