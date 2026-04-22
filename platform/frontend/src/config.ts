const configuredApiBaseUrl = import.meta.env.VITE_API_BASE_URL?.trim()

export const API_BASE_URL = configuredApiBaseUrl || '/api/v1'
export const API_ORIGIN = configuredApiBaseUrl
  ? API_BASE_URL.replace(/\/api\/v1$/, '')
  : window.location.origin
