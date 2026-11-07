import { useState } from 'react'
import { errorMessage, getInstruments, getPrices, getStats, type PriceSeries, type PriceStats } from './api'
import { PriceChart } from './components/PriceChart'
import { StatsTable } from './components/StatsTable'
import { Status } from './components/Status'
import { TickerPicker } from './components/TickerPicker'
import { useAsync } from './useAsync'

const MAX_SELECTED = 3
// A color stays with its ticker while selected (removing one never repaints the others).
const COLORS = ['var(--series-1)', 'var(--series-2)', 'var(--series-3)']

interface Selection {
  ticker: string
  color: string
}

interface TickerData extends Selection {
  series?: PriceSeries
  stats?: PriceStats
  error?: string
}

type ReadyTicker = Required<Omit<TickerData, 'error'>>

async function loadTicker(sel: Selection): Promise<TickerData> {
  try {
    const [series, stats] = await Promise.all([getPrices(sel.ticker), getStats(sel.ticker)])
    return { ...sel, series, stats }
  } catch (err) {
    return { ...sel, error: errorMessage(err) }
  }
}

export default function App() {
  const instruments = useAsync(getInstruments, [])
  const [selected, setSelected] = useState<Selection[]>([])
  const details = useAsync(
    () => Promise.all(selected.map(loadTicker)),
    [selected.map((s) => s.ticker).join()],
  )

  const toggle = (ticker: string) =>
    setSelected((sel) => {
      if (sel.some((s) => s.ticker === ticker)) return sel.filter((s) => s.ticker !== ticker)
      if (sel.length >= MAX_SELECTED) return sel
      const color = COLORS.find((c) => !sel.some((s) => s.color === c))!
      return [...sel, { ticker, color }]
    })

  // Ignore results for tickers removed while a request was in flight.
  const current = (details.data ?? []).filter((d) => selected.some((s) => s.ticker === d.ticker))
  const ready = current.filter((d): d is ReadyTicker => !!d.series && !!d.stats)
  const errors = [...new Set(current.flatMap((d) => (d.error ? [d.error] : [])))]

  return (
    <div className="app">
      <header>
        <h1>Instrument Price Dashboard</h1>
        <p className="muted">Daily closing prices over a 30-day window</p>
      </header>

      <div className="layout">
        <aside>
          <Status loading={instruments.loading} error={instruments.error} onRetry={instruments.retry} />
          {instruments.data && (
            <TickerPicker
              tickers={instruments.data}
              selected={selected.map((s) => s.ticker)}
              max={MAX_SELECTED}
              onToggle={toggle}
            />
          )}
        </aside>

        <main>
          {selected.length === 0 ? (
            <p className="empty">
              Select a ticker to see its price chart. Pick up to {MAX_SELECTED} to compare.
            </p>
          ) : (
            <>
              <ul className="chips">
                {selected.map((s) => (
                  <li key={s.ticker}>
                    <span className="swatch" style={{ background: s.color }} />
                    {s.ticker}
                    <button onClick={() => toggle(s.ticker)} aria-label={`Remove ${s.ticker}`}>
                      ×
                    </button>
                  </li>
                ))}
              </ul>

              <Status loading={details.loading} error={details.error} onRetry={details.retry} />
              {errors.map((error) => (
                <Status key={error} loading={false} error={error} onRetry={details.retry} />
              ))}

              {ready.length > 0 && (
                <>
                  <PriceChart
                    series={ready.map((d) => ({ ticker: d.ticker, color: d.color, prices: d.series.prices }))}
                  />
                  <StatsTable rows={ready.map((d) => ({ stats: d.stats, color: d.color }))} />
                </>
              )}
            </>
          )}
        </main>
      </div>
    </div>
  )
}
