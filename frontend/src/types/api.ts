// Базовые типы для API

export interface User {
  entity_id: number
  username: string
  email: string
  role: 'user' | 'volunteer' | 'moderator' | 'official' | 'admin'
  reputation: number
  avatar_url?: string
  created_at: string
}

export interface Problem {
  entity_id: number
  title: string
  description: string
  status: 'pending' | 'verified' | 'in_progress' | 'resolved' | 'rejected'
  category: string
  latitude: number
  longitude: number
  address: string
  zone_entity_id?: number
  zone_name?: string
  author_entity_id: number
  author?: User
  truth_score: number
  upvotes: number
  downvotes: number
  comments_count: number
  views_count: number
  created_at: string
  updated_at: string
  media?: Media[]
}

export interface Media {
  entity_id: number
  problem_entity_id: number
  media_type: 'image' | 'video'
  url: string
  thumbnail_url?: string
  category: 'before' | 'during' | 'after' | 'other'
  order_index: number
  created_at: string
}

export interface Comment {
  entity_id: number
  problem_entity_id: number
  author_entity_id: number
  author?: User
  content: string
  parent_entity_id?: number
  is_flagged: boolean
  is_hidden: boolean
  created_at: string
  replies?: Comment[]
}

export interface Zone {
  entity_id: number
  name: string
  zone_type: string
  parent_entity_id?: number
  latitude: number
  longitude: number
  created_at: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  offset: number
  limit: number
}

export interface ApiError {
  detail: string
  status_code: number
}
