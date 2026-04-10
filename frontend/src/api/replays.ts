import api from './index'

export const replayApi = {
  list: (params?: any) => api.get('/replays', { params }),
  create: (data: any) => api.post('/replays', data),
  get: (id: number) => api.get(`/replays/${id}`),
  getResults: (id: number, params?: any) => api.get(`/replays/${id}/results`, { params }),
  getReportUrl: (id: number) => `/api/v1/replays/${id}/report`,
}
