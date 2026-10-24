import type { Author } from '@/types/user'

export interface Tag {
  id: number
  name: string
  slug: string
}

export interface Post {
  id: number
  title: string
  slug: string
  excerpt: string
  content: string
  created_at: string
  updated_at: string
  author: Author
  tags: Tag[]
  like_count: number
  liked_by_current_user: boolean
}

export interface Page<T> {
  items: T[]
  page: number
  limit: number
  total: number
  total_pages: number
}

export interface PostPayload {
  title: string
  excerpt: string
  content: string
  tags: string[]
}

export interface LikeResult {
  liked: boolean
  like_count: number
}

export interface PostQuery {
  page?: number
  limit?: number
  search?: string
  tag?: string
}
