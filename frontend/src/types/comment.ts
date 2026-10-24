import type { Page } from '@/types/post'
import type { Author } from '@/types/user'

export interface Comment {
  id: number
  post_id: number
  body: string
  created_at: string
  updated_at: string
  author: Author
  like_count: number
  liked_by_current_user: boolean
}

export type CommentPage = Page<Comment>
