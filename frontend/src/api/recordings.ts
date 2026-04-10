import api from './index'

export const recordingApi = {
  listSessions: (params?: any) => api.get('/sessions', { params }),
  createSession: (data: any) => api.post('/sessions', data),
  syncSession: (sessionId: number, data: any) => api.post(`/sessions/${sessionId}/sync`, data),
  listRecordings: (sessionId: number, params?: any) => api.get(`/sessions/${sessionId}/recordings`, { params }),
  listAllRecordings: (params?: any) => api.get('/sessions/recordings/all', { params }),
  getRecording: (id: number) => api.get(`/sessions/recordings/${id}`),
}
