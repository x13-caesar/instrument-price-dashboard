interface Props {
  loading: boolean
  error?: string
  onRetry: () => void
}

/** Shared loading / error message. Renders nothing once data is ready. */
export function Status({ loading, error, onRetry }: Props) {
  if (error) {
    return (
      <div className="status error" role="alert">
        <span>{error}</span>
        <button onClick={onRetry}>Retry</button>
      </div>
    )
  }
  if (loading) return <div className="status">Loading…</div>
  return null
}
