import { useState } from 'react'

interface Props {
  tickers: string[]
  selected: string[]
  max: number
  onToggle: (ticker: string) => void
}

export function TickerPicker({ tickers, selected, max, onToggle }: Props) {
  const [query, setQuery] = useState('')
  const q = query.trim().toUpperCase()
  const matches = tickers.filter((t) => t.includes(q))
  const full = selected.length >= max

  // Enter picks the first match, or looks up the typed ticker as-is
  // (the API then reports whether it exists).
  const submit = (e: React.FormEvent) => {
    e.preventDefault()
    const ticker = matches[0] ?? q
    if (ticker && !selected.includes(ticker)) onToggle(ticker)
  }

  return (
    <div className="picker">
      <form onSubmit={submit}>
        <input
          type="search"
          placeholder="Search tickers…"
          aria-label="Search tickers"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
      </form>
      <p className="muted">
        {selected.length}/{max} selected{full && ' — remove one to add another'}
      </p>
      {matches.length === 0 && <p className="muted">No match. Press Enter to look up “{q}”.</p>}
      <ul className="ticker-list">
        {matches.map((t) => {
          const isSelected = selected.includes(t)
          return (
            <li key={t}>
              <button
                aria-pressed={isSelected}
                disabled={!isSelected && full}
                onClick={() => onToggle(t)}
              >
                {t}
              </button>
            </li>
          )
        })}
      </ul>
    </div>
  )
}
