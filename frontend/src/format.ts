export const formatPrice = (v: number) => v.toFixed(2)

export const formatPct = (v: number | null) => (v === null ? '—' : `${v.toFixed(2)}%`)

/** Like formatPct, with an explicit "+" for gains (returns, % change). */
export const formatChange = (v: number) => `${v > 0 ? '+' : ''}${formatPct(v)}`

export const formatDate = (iso: string) =>
  new Date(`${iso}T00:00`).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
