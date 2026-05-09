/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

interface Window {
  __TRAFFIC_RECORDER_CONFIG__?: {
    VITE_API_BASE_URL?: string
  }
  __AREX_RECORDER_CONFIG__?: {
    VITE_API_BASE_URL?: string
  }
}
