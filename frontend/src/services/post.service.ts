import { api } from '@/services/api'
import type { LikeResult, Page, Post, PostPayload, PostQuery } from '@/types/post'

export const postService = {
  async list(query: PostQuery = {}): Promise<Page<Post>> {
    const { data } = await api.get<Page<Post>>('/posts', { params: query })
    return data
  },

  async get(postId: number | string): Promise<Post> {
    const { data } = await api.get<Post>(`/posts/${postId}`)
    return data
  },

  async create(payload: PostPayload): Promise<Post> {
    const { data } = await api.post<Post>('/posts', payload)
    return data
  },

  async update(postId: number | string, payload: PostPayload): Promise<Post> {
    const { data } = await api.put<Post>(`/posts/${postId}`, payload)
    return data
  },

  async remove(postId: number | string): Promise<void> {
    await api.delete(`/posts/${postId}`)
  },

  async like(postId: number): Promise<LikeResult> {
    const { data } = await api.post<LikeResult>(`/posts/${postId}/like`)
    return data
  },

  async unlike(postId: number): Promise<LikeResult> {
    const { data } = await api.delete<LikeResult>(`/posts/${postId}/like`)
    return data
  },
}
