export interface Period {
  year: number
  month: number // 1..12
}

export function addMonths({ year, month }: Period, delta: number): Period {
  // month es 1..12; Date usa 0..11 internamente.
  const d = new Date(year, month - 1 + delta, 1)
  return { year: d.getFullYear(), month: d.getMonth() + 1 }
}
