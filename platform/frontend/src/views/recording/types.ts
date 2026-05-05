import type { RecordingSubCall } from '@/utils/recording'

export type SessionRow = {
  id: number
  application_id: number
  name: string
  status: string
  total_count: number
  error_message?: string | null
  recording_filter_prefixes?: string[] | null
  created_at: string
}

export type RecordingRow = {
  id: number
  request_method: string
  request_uri: string
  transaction_code?: string | null
  governance_status: string
  duplicate_count?: number | null
  response_status: number | null
  latency_ms: number | null
  sub_calls?: RecordingSubCall[] | string | null
  recorded_at: string
  quality_score?: number | null
  quality_level?: string | null
  quality_recommendation?: string | null
  quality_reasons?: string[]
}

export type RecordingGroupRow = {
  application_id: number
  transaction_code?: string | null
  scene_key?: string | null
  total_count: number
  approved_count: number
  candidate_count: number
  raw_count: number
  latest_recorded_at: string
  representative_recording_id: number
  representative_governance_status: string
  representative_request_method: string
  representative_request_uri: string
}
