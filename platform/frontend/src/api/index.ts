import axios from 'axios'
import { API_BASE_URL } from '@/config'
import { useUserStore } from '@/store/user'

let redirectingToLogin = false

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  withCredentials: true,
})

api.interceptors.request.use((config) => {
  const userStore = useUserStore()
  if (userStore.token) {
    config.headers.Authorization = `Bearer ${userStore.token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const userStore = useUserStore()
    const originalRequest = error.config || {}
    const requestUrl = String(originalRequest.url || '')
    const isAuthRequest = requestUrl.includes('/auth/login') || requestUrl.includes('/auth/refresh')
    if (error.response?.status === 401 && !originalRequest._retry && !isAuthRequest) {
      originalRequest._retry = true
      const refreshed = await userStore.refreshSession()
      if (refreshed) {
        originalRequest.headers = originalRequest.headers || {}
        originalRequest.headers.Authorization = `Bearer ${userStore.token}`
        return api(originalRequest)
      }
    }
    if (error.response?.status === 401) {
      userStore.clearUser()
      if (!redirectingToLogin && window.location.pathname !== '/login') {
        redirectingToLogin = true
        window.location.assign('/login')
      }
    }
    return Promise.reject(error)
  }
)

export default api
