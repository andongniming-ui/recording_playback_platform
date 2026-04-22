import api from './index'

export const userApi = {
  list: (params?: any) => api.get('/users', { params }),
  bulkDelete: (data: { ids: number[] }) => api.post('/users/bulk-delete', data),
  create: (data: any) => api.post('/users', data),
  update: (id: number, data: any) => api.put(`/users/${id}`, data),
  delete: (id: number) => api.delete(`/users/${id}`),
}
