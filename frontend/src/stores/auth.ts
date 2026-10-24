import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

import { getStoredToken, setStoredToken } from '@/services/api'
import { authService } from '@/services/auth.service'
import type { CurrentUser, LoginPayload, RegisterPayload } from '@/types/user'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<CurrentUser | null>(null)
  const token = ref<string | null>(getStoredToken())
  const loading = ref(false)
  const initialised = ref(false)

  const isAuthenticated = computed(() => user.value !== null)

  function setSession(accessToken: string, currentUser: CurrentUser): void {
    token.value = accessToken
    user.value = currentUser
    setStoredToken(accessToken)
  }

  async function login(payload: LoginPayload): Promise<void> {
    loading.value = true
    try {
      const data = await authService.login(payload)
      setSession(data.access_token, data.user)
    } finally {
      loading.value = false
    }
  }

  async function register(payload: RegisterPayload): Promise<void> {
    loading.value = true
    try {
      const data = await authService.register(payload)
      setSession(data.access_token, data.user)
    } finally {
      loading.value = false
    }
  }

  function logout(): void {
    user.value = null
    token.value = null
    setStoredToken(null)
  }

  async function fetchCurrentUser(): Promise<void> {
    if (!token.value) {
      initialised.value = true
      return
    }
    loading.value = true
    try {
      user.value = await authService.me()
    } catch {
      // The token is expired or invalid; treat it as logged out.
      logout()
    } finally {
      loading.value = false
      initialised.value = true
    }
  }

  function setUser(updated: CurrentUser): void {
    user.value = updated
  }

  return {
    user,
    token,
    loading,
    initialised,
    isAuthenticated,
    login,
    register,
    logout,
    fetchCurrentUser,
    setUser,
  }
})
