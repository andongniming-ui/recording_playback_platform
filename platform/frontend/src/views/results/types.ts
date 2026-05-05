import type { RecordingSubCall } from '@/utils/recording'

export type ReplayJobRow = {
  id: number
  name?: string | null
  application_id?: number | null
  status: string
  concurrency: number
  timeout_ms: number
  delay_ms?: number
  total: number
  passed: number
  failed: number
  errored: number
  ignore_fields?: string[] | null
  diff_rules?: Array<{ type: string; path?: string | null }> | null
  assertions?: Array<{ type: string; path?: string | null }> | null
  header_transforms?: Array<{ type: string; key: string }> | null
  use_sub_invocation_mocks?: boolean
  perf_threshold_ms?: number | null
  smart_noise_reduction?: boolean
  retry_count?: number
  webhook_url?: string | null
  created_at: string
  started_at?: string | null
  finished_at?: string | null
}

export type ReplayResultRow = {
  id: number
  test_case_id?: number | null
  use_sub_invocation_mocks?: boolean
  source_recording_id?: number | null
  source_recording_transaction_code?: string | null
  source_recording_scene_key?: string | null
  source_recording_sub_call_count?: number | null
  request_method?: string | null
  request_uri?: string | null
  actual_status_code?: number | null
  actual_response?: string | null
  expected_response?: string | null
  diff_result?: string | null
  diff_score?: number | null
  assertion_results?: string | null
  status: string
  latency_ms?: number | null
  failure_category?: string | null
  failure_reason?: string | null
  created_at: string
  transaction_code?: string | null
}

export type RuleSuggestion = {
  key: string
  field: string
  path: string
  raw_path: string
  change_types: string[]
}

export type ReplayAnalysisData = {
  categories?: Record<string, { count?: number; percentage?: number; description?: string; examples?: string[] }>
}

export type SourceTestCase = {
  id: number
  source_recording_id?: number | null
}

export type SourceRecording = {
  id: number
  request_method: string
  request_uri: string
  transaction_code?: string | null
  governance_status: string
  sub_calls?: RecordingSubCall[] | string | null
}
