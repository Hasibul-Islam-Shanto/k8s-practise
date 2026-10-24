export interface Author {
  id: number
  full_name: string
  username: string
  avatar_url: string | null
}

export interface CurrentUser extends Author {
  email: string
  bio: string | null
  created_at: string
}

export interface UserProfile extends Author {
  bio: string | null
  created_at: string
  post_count: number
  total_likes_received: number
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: CurrentUser
}

export interface RegisterPayload {
  full_name: string
  username: string
  email: string
  password: string
  confirm_password: string
  bio?: string | null
}

export interface LoginPayload {
  identifier: string
  password: string
}

export interface ProfileUpdatePayload {
  full_name?: string
  bio?: string | null
  avatar_url?: string | null
}
