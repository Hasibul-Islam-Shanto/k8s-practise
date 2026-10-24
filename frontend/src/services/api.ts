import axios, { AxiosError } from 'axios'

const TOKEN_KEY = 'techblog.token'

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api/v1',
  headers: { 'Content-Type': 'application/json' },
})

export function getStoredToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function setStoredToken(token: string | null): void {
  if (token) localStorage.setItem(TOKEN_KEY, token)
  else localStorage.removeItem(TOKEN_KEY)
}

api.interceptors.request.use((config) => {
  const token = getStoredToken()
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

/** Set by the router once it exists, so this module doesn't import the router
 *  and create a cycle. */
let onUnauthorized: (() => void) | null = null

export function setUnauthorizedHandler(handler: () => void): void {
  onUnauthorized = handler
}

api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    // An expired or revoked token should drop the session rather than leave the
    // UI in a half-authenticated state. A failed login is not a session problem,
    // so it is excluded.
    const url = error.config?.url ?? ''
    const isLoginAttempt = url.includes('/auth/login') || url.includes('/auth/register')
    if (error.response?.status === 401 && !isLoginAttempt) {
      setStoredToken(null)
      onUnauthorized?.()
    }
    return Promise.reject(error)
  },
)

/** Pull a human-readable message out of a FastAPI error response.
 *  FastAPI returns `{detail: string}` for raised errors and
 *  `{detail: [{loc, msg, ...}]}` for validation failures. */
export function errorMessage(error: unknown, fallback = 'Something went wrong. Please try again.'): string {
  if (!axios.isAxiosError(error)) return fallback
  if (error.code === 'ERR_NETWORK') return 'Unable to reach the server. Please check your connection.'

  const detail = (error.response?.data as { detail?: unknown } | undefined)?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    const first = detail[0] as { msg?: string } | undefined
    if (first?.msg) return first.msg.replace(/^Value error, /, '')
  }
  return fallback
}

export function fieldErrors(error: unknown): Record<string, string> {
  if (!axios.isAxiosError(error)) return {}
  const detail = (error.response?.data as { detail?: unknown } | undefined)?.detail
  if (!Array.isArray(detail)) return {}

  const errors: Record<string, string> = {}
  for (const item of detail as { loc?: unknown[]; msg?: string }[]) {
    const field = item.loc?.at(-1)
    if (typeof field === 'string' && item.msg && !errors[field]) {
      errors[field] = item.msg.replace(/^Value error, /, '')
    }
  }
  return errors
}
