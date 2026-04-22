import api from './index'

export const statsApi = {
  trend: (params?: any) => api.get('/stats/trend', { params }),
  summary: () => api.get('/stats/summary'),
  appSummary: () => api.get('/stats/app-summary'),
  failureTypes: (params?: any) => api.get('/stats/failure-types', { params }),
  recentJobs: (params?: any) => api.get('/stats/recent-jobs', { params }),
}
