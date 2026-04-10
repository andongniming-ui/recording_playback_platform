import api from './index'

export const suiteApi = {
  list: (params?: any) => api.get('/suites', { params }),
  create: (data: any) => api.post('/suites', data),
  get: (id: number) => api.get(`/suites/${id}`),
  update: (id: number, data: any) => api.put(`/suites/${id}`, data),
  delete: (id: number) => api.delete(`/suites/${id}`),
  setCases: (id: number, data: any) => api.put(`/suites/${id}/cases`, data),
  run: (id: number) => api.post(`/suites/${id}/run`),
}
