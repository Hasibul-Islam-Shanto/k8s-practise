import { api } from '@/services/api'
import type { Page, Post } from '@/types/post'
import type { CurrentUser, ProfileUpdatePayload, UserProfile } from '@/types/user'

export const userService = {
  async profile(username: string): Promise<UserProfile> {
    const { data } = await api.get<UserProfile>(`/users/${username}`)
    return data
  },

  async posts(username: string, page = 1, limit = 10): Promise<Page<Post>> {
    const { data } = await api.get<Page<Post>>(`/users/${username}/posts`, {
      params: { page, limit },
    })
    return data
  },

  async updateOwnProfile(payload: ProfileUpdatePayload): Promise<CurrentUser> {
    const { data } = await api.put<CurrentUser>('/users/me', payload)
    return data
  },
}
