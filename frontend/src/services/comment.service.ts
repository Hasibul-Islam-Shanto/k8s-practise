import { api } from '@/services/api'
import type { Comment, CommentPage } from '@/types/comment'
import type { LikeResult } from '@/types/post'

export const commentService = {
  async list(postId: number, query: { page?: number; limit?: number } = {}): Promise<CommentPage> {
    const { data } = await api.get<CommentPage>(`/posts/${postId}/comments`, { params: query })
    return data
  },

  async create(postId: number, body: string): Promise<Comment> {
    const { data } = await api.post<Comment>(`/posts/${postId}/comments`, { body })
    return data
  },

  async update(postId: number, commentId: number, body: string): Promise<Comment> {
    const { data } = await api.put<Comment>(`/posts/${postId}/comments/${commentId}`, { body })
    return data
  },

  async remove(postId: number, commentId: number): Promise<void> {
    await api.delete(`/posts/${postId}/comments/${commentId}`)
  },

  async like(postId: number, commentId: number): Promise<LikeResult> {
    const { data } = await api.post<LikeResult>(`/posts/${postId}/comments/${commentId}/like`)
    return data
  },

  async unlike(postId: number, commentId: number): Promise<LikeResult> {
    const { data } = await api.delete<LikeResult>(`/posts/${postId}/comments/${commentId}/like`)
    return data
  },
}
