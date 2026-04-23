/**
 * Format an ISO datetime string to local time string.
 * Strings without an explicit timezone are treated as local wall-clock time.
 */
export function formatDateTime(value?: string | null): string {
  if (!value) return '-'
  const normalized = value.endsWith('Z') || /[+-]\d{2}:\d{2}$/.test(value)
    ? value
    : value.replace(' ', 'T')
  const d = new Date(normalized)
  if (isNaN(d.getTime())) return value
  return d.toLocaleString('zh-CN', { hour12: false }).replace(/\//g, '-')
}
