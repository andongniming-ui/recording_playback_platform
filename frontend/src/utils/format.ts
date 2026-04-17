/**
 * Format an ISO datetime string (possibly UTC) to local time string.
 * Treats strings without timezone suffix as UTC.
 */
export function formatDateTime(value?: string | null): string {
  if (!value) return '-'
  const normalized = value.endsWith('Z') || /[+-]\d{2}:\d{2}$/.test(value) ? value : value + 'Z'
  const d = new Date(normalized)
  if (isNaN(d.getTime())) return value
  return d.toLocaleString('zh-CN', { hour12: false }).replace(/\//g, '-')
}
