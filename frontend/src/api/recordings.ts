import api from './index'

export const recordingApi = {
  listSessions: (params?: any) => api.get('/sessions', { params }),
  createSession: (data: any) => api.post('/sessions', data),
  getSession: (sessionId: number) => api.get(`/sessions/${sessionId}`),
  startSession: (sessionId: number) => api.post(`/sessions/${sessionId}/start`, {}),
  stopSession: (sessionId: number, data: any) => api.post(`/sessions/${sessionId}/stop`, data),
  syncSession: (sessionId: number, data: any) => api.post(`/sessions/${sessionId}/sync`, data),
  listRecordings: (sessionId: number, params?: any) => api.get(`/sessions/${sessionId}/recordings`, { params }),
  listAllRecordings: (params?: any) => api.get('/sessions/recordings/all', { params }),
  listRecordingGroups: (params?: any) => api.get('/sessions/recordings/groups', { params }),
  getRecording: (id: number) => api.get(`/sessions/recordings/${id}`),
  updateRecording: (id: number, data: any) => api.patch(`/sessions/recordings/${id}`, data),
  deleteSession: (sessionId: number) => api.delete(`/sessions/${sessionId}`),
}
