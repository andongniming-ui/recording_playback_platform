import api from './index'

export const applicationApi = {
  list: (params?: any) => api.get('/applications', { params }),
  create: (data: any) => api.post('/applications', data),
  get: (id: number) => api.get(`/applications/${id}`),
  update: (id: number, data: any) => api.put(`/applications/${id}`, data),
  delete: (id: number) => api.delete(`/applications/${id}`),
  testConnection: (id: number) => api.post(`/applications/${id}/test-connection`),
  mountAgent: (id: number) => api.post(`/applications/${id}/mount-agent`),
  unmountAgent: (id: number) => api.post(`/applications/${id}/unmount-agent`),
  getAgentStatus: (id: number) => api.get(`/applications/${id}/agent-status`),
}
