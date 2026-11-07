import axios from 'axios'

export interface PricePoint {
  date: string // YYYY-MM-DD
  price: number
}

export interface PriceSeries {
  ticker: string
  prices: PricePoint[]
}

export interface PriceStats {
  ticker: string
  start_date: string
  end_date: string
  first_price: number
  last_price: number
  total_return_pct: number
  daily_volatility_pct: number | null
  max_drawdown_pct: number
}

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000/api',
  timeout: 10_000,
})

const get = <T>(url: string) => api.get<T>(url).then((res) => res.data)
const tickerPath = (ticker: string) => `/prices/${encodeURIComponent(ticker)}`

export const getInstruments = () => get<string[]>('/instruments')
export const getPrices = (ticker: string) => get<PriceSeries>(tickerPath(ticker))
export const getStats = (ticker: string) => get<PriceStats>(`${tickerPath(ticker)}/stats`)

export function errorMessage(err: unknown): string {
  if (axios.isAxiosError(err)) {
    if (!err.response) return 'Cannot reach the API. Is the backend running on port 8000?'
    return err.response.data?.detail ?? `Request failed (${err.response.status})`
  }
  return 'Something went wrong.'
}
