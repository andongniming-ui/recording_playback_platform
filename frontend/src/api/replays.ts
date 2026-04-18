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
}

export interface SubCallDiffResult {
  recorded: SubCallDiffItem[]
  replayed: SubCallDiffItem[]
  pairs: SubCallDiffPair[]
}

export const replayApi = {
  list: (params?: any) => api.get('/replays', { params }),
  create: (data: any) => api.post('/replays', data),
  get: (id: number) => api.get(`/replays/${id}`),
  getResult: (id: number) => api.get(`/replays/results/${id}`),
  getResults: (id: number, params?: any) => api.get(`/replays/${id}/results`, { params }),
  getReport: (id: number) => api.get(`/replays/${id}/report`, { responseType: 'blob' }),
  getReportUrl: (id: number) => `${API_BASE_URL}/replays/${id}/report`,
  getAnalysis: (id: number) => api.get(`/replays/${id}/analysis`),
  getSubCallDiff: (resultId: number) => api.get<SubCallDiffResult>(`/replays/results/${resultId}/sub-call-diff`),
}
