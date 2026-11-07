import { useEffect, useState } from 'react'
import { errorMessage } from './api'

interface AsyncState<T> {
  data?: T
  error?: string
  loading: boolean
}

/** Run `load` whenever `deps` change; ignores responses from stale runs. */
export function useAsync<T>(load: () => Promise<T>, deps: unknown[]) {
  const [state, setState] = useState<AsyncState<T>>({ loading: true })
  const [attempt, setAttempt] = useState(0)

  useEffect(() => {
    let stale = false
    setState((s) => ({ ...s, loading: true, error: undefined }))
    load().then(
      (data) => !stale && setState({ data, loading: false }),
      (err) => !stale && setState({ error: errorMessage(err), loading: false }),
    )
    return () => {
      stale = true
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps, attempt])

  return { ...state, retry: () => setAttempt((n) => n + 1) }
}
