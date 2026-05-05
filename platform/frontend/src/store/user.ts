import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'
import { API_BASE_URL } from '@/config'

type LoginPayload = {
  access_token: string
  username: string
  role: string
}

export const useUserStore = defineStore('user', () => {
  const token = ref('')
  const username = ref(localStorage.getItem('username') || '')
  const role = ref(localStorage.getItem('role') || '')
  const refreshing = ref(false)
  let refreshPromise: Promise<boolean> | null = null

  function setUser(payload: LoginPayload) {
    token.value = payload.access_token
    username.value = payload.username
    role.value = payload.role
    localStorage.setItem('username', payload.username)
    localStorage.setItem('role', payload.role)
  }

  function clearUser() {
    token.value = ''
    username.value = ''
    role.value = ''
    localStorage.removeItem('username')
    localStorage.removeItem('role')
  }

  async function refreshSession() {
    if (refreshPromise) return refreshPromise
    refreshing.value = true
    refreshPromise = (async () => {
      try {
        const resp = await axios.post(`${API_BASE_URL}/auth/refresh`, undefined, {
          withCredentials: true,
        })
        setUser({
          access_token: resp.data.access_token,
          username: resp.data.username,
          role: resp.data.role || 'viewer',
        })
        return true
      } catch {
        clearUser()
        return false
      } finally {
        refreshing.value = false
        refreshPromise = null
      }
    })()
    return refreshPromise
  }

  async function logout() {
    try {
      await axios.post(`${API_BASE_URL}/auth/logout`, undefined, { withCredentials: true })
    } catch {
      // Local logout must still complete if the server is unreachable.
    }
    clearUser()
  }

  return { token, username, role, refreshing, setUser, clearUser, refreshSession, logout }
})
