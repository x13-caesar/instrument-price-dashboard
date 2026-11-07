import type { PriceStats } from '../api'
import { formatChange, formatPct, formatPrice } from '../format'

export function StatsTable({ rows }: { rows: { stats: PriceStats; color: string }[] }) {
  return (
    <table className="stats">
      <thead>
        <tr>
          <th>Ticker</th>
          <th>First → last</th>
          <th>Total return</th>
          <th>Daily volatility</th>
          <th>Max drawdown</th>
        </tr>
      </thead>
      <tbody>
        {rows.map(({ stats: s, color }) => (
          <tr key={s.ticker}>
            <td>
              <span className="swatch" style={{ background: color }} />
              {s.ticker}
            </td>
            <td>
              {formatPrice(s.first_price)} → {formatPrice(s.last_price)}
            </td>
            <td>{formatChange(s.total_return_pct)}</td>
            <td>{formatPct(s.daily_volatility_pct)}</td>
            <td>{formatPct(s.max_drawdown_pct)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
