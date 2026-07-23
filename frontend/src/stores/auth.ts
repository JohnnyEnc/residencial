import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import api from '../api/client'
import type { User, UserRole } from '../types'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('token'))
  const loading = ref(false)

  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const role = computed<UserRole | null>(() => user.value?.role ?? null)

  async function login(email: string, password: string) {
    loading.value = true
    try {
      const { data } = await api.post('/auth/login', { email, password })
      // Solo persistir token si /me también responde (evita estado a medias en Render).
      const previous = api.defaults.headers.common.Authorization
      api.defaults.headers.common.Authorization = `Bearer ${data.access_token}`
      try {
        const me = await api.get<User>('/auth/me')
        token.value = data.access_token
        localStorage.setItem('token', data.access_token)
        user.value = me.data
      } finally {
        if (previous) api.defaults.headers.common.Authorization = previous
        else delete api.defaults.headers.common.Authorization
      }
    } finally {
      loading.value = false
    }
  }

  async function fetchMe() {
    if (!token.value) return
    const { data } = await api.get<User>('/auth/me')
    user.value = data
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
  }

  function homePath() {
    if (role.value === 'admin') return '/admin'
    if (role.value === 'staff') return '/staff'
    if (role.value === 'resident') return '/app'
    return '/login'
  }

  return { user, token, loading, isAuthenticated, role, login, fetchMe, logout, homePath }
})
