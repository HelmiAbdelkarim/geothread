export type BackendSortStrategy = 'hot' | 'new' | 'top' | 'rising' | 'controversial'
export type SortStrategy = BackendSortStrategy | 'closest'
export type VoteDirection = 'up' | 'down' | 'remove'

export interface Redditor {
  user_id: number
  username: string
  email: string
  created_at: string
  post_karma: number
  comment_karma: number
  total_karma?: number
}

export interface UserStats {
  user_id: number
  username: string
  post_karma: number
  comment_karma: number
  total_karma: number
  subscriptions: number
  posts_created: number
  feed_size: number
  feed_sort: BackendSortStrategy
}

export interface Subreddit {
  subreddit_id: number
  name: string
  description: string
  created_at: string
  subscriber_count: number
}

export interface SubredditRecommendation {
  subreddit_id: number
  subreddit_name: string
  total_score: number
  distance_km: number | null
  distance_score: number
  activity_score: number
  relevance_score: number
  reason: string
}

export interface Post {
  post_id: number
  author_id: number
  subreddit_id: number
  title: string
  content: string
  timestamp: string
  upvotes: number
  downvotes: number
  score?: number
  vote_ratio?: number
  comments: number
  author_username?: string
  subreddit_name?: string
  user_vote?: number
  image_url?: string
  latitude?: number
  longitude?: number
  location_name?: string
  distance_km?: number
}

export interface Comment {
  comment_id?: number
  id?: number
  content: string
  author_id: number | null
  author_username?: string
  post_id: number
  parent_comment_id: number | null
  created_at: string
  updated_at: string
  is_edited: boolean
  is_deleted: boolean
  upvotes?: number
  downvotes?: number
  score?: number
  user_vote?: number
  children: Comment[]
}

export interface CommentTree {
  post_id: number
  total_comments: number
  max_depth: number
  comments: Comment[]
}

export interface MessageResponse {
  message: string
  success: boolean
}
