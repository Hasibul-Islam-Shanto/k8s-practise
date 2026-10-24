import { api } from '@/services/api'
import type { AuthResponse, CurrentUser, LoginPayload, RegisterPayload } from '@/types/user'

export const authService = {
  async register(payload: RegisterPayload): Promise<AuthResponse> {
    const { data } = await api.post<AuthResponse>('/auth/register', payload)
    return data
  },

  async login(payload: LoginPayload): Promise<AuthResponse> {
    const { data } = await api.post<AuthResponse>('/auth/login', payload)
    return data
  },

  async me(): Promise<CurrentUser> {
    const { data } = await api.get<CurrentUser>('/auth/me')
    return data
  },
}
