import api from './index'

export const testCaseApi = {
  list: (params?: any) => api.get('/test-cases', { params }),
  bulkDelete: (data: { ids: number[] }) => api.post('/test-cases/bulk-delete', data),
  create: (data: any) => api.post('/test-cases', data),
  get: (id: number) => api.get(`/test-cases/${id}`),
  update: (id: number, data: any) => api.put(`/test-cases/${id}`, data),
  delete: (id: number) => api.delete(`/test-cases/${id}`),
  fromRecording: (data: any) => api.post('/test-cases/from-recording', data),
  clone: (id: number) => api.post(`/test-cases/${id}/clone`),
  exportCases: (params?: any) => api.get('/test-cases/export', { params }),
  addToSuite: (id: number, data: any) => api.post(`/test-cases/${id}/add-to-suite`, data),
  batchCheck: (data: { recording_ids: number[] }) =>
    api.post('/test-cases/batch-check', data),
  batchFromRecordings: (data: { recording_ids: number[]; prefix: string }) =>
    api.post('/test-cases/batch-from-recordings', data),
}
