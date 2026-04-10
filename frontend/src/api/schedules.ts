import api from './index'

export const scheduleApi = {
  list: (params?: any) => api.get('/schedules', { params }),
  create: (data: any) => api.post('/schedules', data),
  get: (id: number) => api.get(`/schedules/${id}`),
  update: (id: number, data: any) => api.put(`/schedules/${id}`, data),
  delete: (id: number) => api.delete(`/schedules/${id}`),
  trigger: (id: number) => api.post(`/schedules/${id}/trigger`),
}
