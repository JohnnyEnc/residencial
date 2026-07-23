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
      token.value = data.access_token
      localStorage.setItem('token', data.access_token)
      await fetchMe()
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
    return '/app'
  }

  return { user, token, loading, isAuthenticated, role, login, fetchMe, logout, homePath }
})
