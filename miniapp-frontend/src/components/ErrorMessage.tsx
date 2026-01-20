/**
 * Error message component
 */
interface ErrorMessageProps {
  message: string
  onRetry?: () => void
  onDismiss?: () => void
}

const ErrorMessage = ({ message, onRetry, onDismiss }: ErrorMessageProps) => {
  return (
    <div className="ios-card p-4 border-l-4 border-danger">
      <div className="flex items-start">
        <svg
          className="w-6 h-6 text-danger mr-3 flex-shrink-0"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
        <div className="flex-1">
          <h3 className="font-semibold text-danger mb-1">Error</h3>
          <p className="text-sm text-text-secondary-light dark:text-text-secondary-dark">
            {message}
          </p>
          {(onRetry || onDismiss) && (
            <div className="flex gap-2 mt-3">
              {onRetry && (
                <button
                  onClick={onRetry}
                  className="text-sm text-primary font-medium"
                >
                  Try Again
                </button>
              )}
              {onDismiss && (
                <button
                  onClick={onDismiss}
                  className="text-sm text-text-secondary-light dark:text-text-secondary-dark"
                >
                  Dismiss
                </button>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default ErrorMessage
