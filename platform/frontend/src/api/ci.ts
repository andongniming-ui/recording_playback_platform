import api from './index'

export const ciApi = {
  listTokens: (params?: any) => api.get('/ci/tokens', { params }),
  createToken: (data: any) => api.post('/ci/tokens', data),
  revokeToken: (id: number) => api.delete(`/ci/tokens/${id}`),
  trigger: (data: any) => api.post('/ci/trigger', data),
  getResult: (jobId: number) => api.get(`/ci/result/${jobId}`),
}
