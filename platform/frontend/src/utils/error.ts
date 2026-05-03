/**
 * Extract a human-readable error message from an Axios error response.
 * Backend uses `detail` (FastAPI default); fall back to `message` for
 * older or third-party endpoints, then to the provided fallback string.
 */
export function extractError(error: unknown, fallback: string): string {
  if (error && typeof error === 'object' && 'response' in error) {
    const data = (error as any).response?.data
    if (data?.detail) return String(data.detail)
    if (data?.message) return String(data.message)
  }
  return fallback
}
