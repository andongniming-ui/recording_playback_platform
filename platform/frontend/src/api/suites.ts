import api from './index'

export const suiteApi = {
  list: (params?: any) => api.get('/suites', { params }),
  bulkDelete: (data: { ids: number[] }) => api.post('/suites/bulk-delete', data),
  create: (data: any) => api.post('/suites', data),
  autoSmoke: (data: any) => api.post('/suites/auto-smoke', data),
  get: (id: number) => api.get(`/suites/${id}`),
  update: (id: number, data: any) => api.put(`/suites/${id}`, data),
  delete: (id: number) => api.delete(`/suites/${id}`),
  setCases: (id: number, data: any) => api.put(`/suites/${id}/cases`, data),
  run: (id: number, data?: any) => api.post(`/suites/${id}/run`, data),
}
