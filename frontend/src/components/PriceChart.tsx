import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import type { PricePoint } from '../api'
import { formatChange, formatDate, formatPrice } from '../format'

export interface ChartSeries {
  ticker: string
  color: string
  prices: PricePoint[]
}

type Row = { date: string } & Record<string, number | string>

/**
 * One ticker: closing price. Several tickers: % change since the first day,
 * so instruments with very different price levels share one readable axis.
 */
export function PriceChart({ series }: { series: ChartSeries[] }) {
  const compare = series.length > 1
  const format = (v: number) => (compare ? formatChange(v) : formatPrice(v))

  const rows = new Map<string, Row>()
  for (const { ticker, prices } of series) {
    const base = prices[0]?.price
    for (const { date, price } of prices) {
      const row: Row = rows.get(date) ?? { date }
      row[ticker] = compare ? (price / base - 1) * 100 : price
      rows.set(date, row)
    }
  }
  const data = [...rows.values()].sort((a, b) => a.date.localeCompare(b.date))

  return (
    <figure className="chart">
      <figcaption>
        {compare ? 'Change since first day (%)' : `${series[0].ticker} closing price`}
      </figcaption>
      <ResponsiveContainer width="100%" height={360}>
        <LineChart data={data} margin={{ top: 8, right: 16, bottom: 0, left: 0 }}>
          <CartesianGrid stroke="var(--grid)" vertical={false} />
          <XAxis
            dataKey="date"
            tickFormatter={formatDate}
            stroke="var(--axis)"
            tick={{ fill: 'var(--text-muted)', fontSize: 12 }}
            minTickGap={24}
          />
          <YAxis
            domain={['auto', 'auto']}
            tickFormatter={(v: number) => (compare ? `${v}%` : String(v))}
            stroke="var(--axis)"
            tick={{ fill: 'var(--text-muted)', fontSize: 12 }}
            width={56}
          />
          {compare && <ReferenceLine y={0} stroke="var(--axis)" />}
          <Tooltip
            formatter={(v) => format(Number(v))}
            labelFormatter={(label) => formatDate(String(label))}
            contentStyle={{
              background: 'var(--surface)',
              border: '1px solid var(--border)',
              borderRadius: 6,
            }}
            labelStyle={{ color: 'var(--text-secondary)' }}
            itemStyle={{ color: 'var(--text)' }}
          />
          {compare && (
            <Legend formatter={(value) => <span className="legend-label">{value}</span>} />
          )}
          {series.map(({ ticker, color }) => (
            <Line
              key={ticker}
              dataKey={ticker}
              stroke={color}
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4 }}
              isAnimationActive={false}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </figure>
  )
}
