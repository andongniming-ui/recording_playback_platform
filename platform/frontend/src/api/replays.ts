import api from './index'
import { API_BASE_URL } from '@/config'

export interface DiffRule {
  type: 'ignore' | 'numeric_tolerance' | 'regex_match' | 'type_only'
  path?: string
  tolerance?: number
  pattern?: string
  key?: string
  field?: string
}

export interface AssertionRule {
  type: 'status_code_eq' | 'response_not_empty' | 'json_path_eq' | 'json_path_contains' | 'json_path_exists' | 'json_path_regex' | 'diff_score_lte'
  path?: string
  value?: string
  pattern?: string
}

export interface HeaderTransform {
  type: 'replace' | 'remove' | 'add'
  key: string
  value?: string
}

export interface SubCallDiffItem {
  type?: string | null
  operation?: string | null
  request?: unknown
  response?: unknown
}

export interface SubCallDiffPair {
  index: number
  type: string
  recorded: SubCallDiffItem | null
  replayed: SubCallDiffItem | null
  side: 'both' | 'recorded_only' | 'replayed_only'
  response_matched: boolean | null
  has_diff?: boolean
  diff_result?: string | null
}

export interface SubCallDiffResult {
  recorded: SubCallDiffItem[]
  replayed: SubCallDiffItem[]
  pairs: SubCallDiffPair[]
}

export interface ReplayAuditLog {
  id: number
  job_id: number
  result_id?: number | null
  test_case_id?: number | null
  application_id?: number | null
  level: string
  event_type: string
  target_url?: string | null
  request_method?: string | null
  request_uri?: string | null
  transaction_code?: string | null
  actual_status_code?: number | null
  latency_ms?: number | null
  message?: string | null
  detail?: string | null
  created_at: string
}

export const replayApi = {
  list: (params?: any) => api.get('/replays', { params }),
  bulkDelete: (data: { ids: number[] }) => api.post('/replays/bulk-delete', data),
  create: (data: any) => api.post('/replays', data),
  get: (id: number) => api.get(`/replays/${id}`),
  delete: (id: number) => api.delete(`/replays/${id}`),
  getResult: (id: number) => api.get(`/replays/results/${id}`),
  getResults: (id: number, params?: any) => api.get(`/replays/${id}/results`, { params }),
  getReport: (id: number) => api.get(`/replays/${id}/report`, { responseType: 'blob' }),
  getReportUrl: (id: number) => `${API_BASE_URL}/replays/${id}/report`,
  getAnalysis: (id: number) => api.get(`/replays/${id}/analysis`),
  getRuleSuggestions: (resultId: number) => api.get(`/replays/results/${resultId}/rule-suggestions`),
  applyRuleSuggestion: (resultId: number, data: { suggestion_key: string; target: 'job_ignore_fields' | 'application_default_ignore_fields' }) =>
    api.post(`/replays/results/${resultId}/rule-suggestions/apply`, data),
  getSubCallDiff: (resultId: number) => api.get<SubCallDiffResult>(`/replays/results/${resultId}/sub-call-diff`),
  getAuditLogs: (jobId: number, params?: any) => api.get<ReplayAuditLog[]>(`/replays/${jobId}/audit-logs`, { params }),
}
