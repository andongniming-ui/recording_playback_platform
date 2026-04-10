import api from './index'

export const compareApi = {
  list: (params?: any) => api.get('/compare-rules', { params }),
  create: (data: any) => api.post('/compare-rules', data),
  update: (id: number, data: any) => api.put(`/compare-rules/${id}`, data),
  delete: (id: number) => api.delete(`/compare-rules/${id}`),
}
