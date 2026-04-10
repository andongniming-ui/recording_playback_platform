import api from './index'

export const testCaseApi = {
  list: (params?: any) => api.get('/test-cases', { params }),
  create: (data: any) => api.post('/test-cases', data),
  get: (id: number) => api.get(`/test-cases/${id}`),
  update: (id: number, data: any) => api.put(`/test-cases/${id}`, data),
  delete: (id: number) => api.delete(`/test-cases/${id}`),
  fromRecording: (data: any) => api.post('/test-cases/from-recording', data),
  clone: (id: number) => api.post(`/test-cases/${id}/clone`),
  exportCases: (params?: any) => api.get('/test-cases/export', { params }),
  addToSuite: (id: number, data: any) => api.post(`/test-cases/${id}/add-to-suite`, data),
}
