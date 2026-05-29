import type { Post, Redditor, Subreddit } from '../types'
import { apiRequest } from './api'

export interface SearchResponse {
  posts: Post[]
  subreddits: Subreddit[]
  users: Redditor[]
}

export const searchService = {
  all: (q: string, limit = 10) =>
    apiRequest<SearchResponse>('/search/', { query: { q, limit } }),
  posts: (q: string, limit = 25) =>
    apiRequest<Post[]>('/search/posts', { query: { q, limit } }),
  subreddits: (q: string, limit = 25) =>
    apiRequest<Subreddit[]>('/search/subreddits', { query: { q, limit } }),
  users: (q: string, limit = 25) =>
    apiRequest<Redditor[]>('/search/users', { query: { q, limit } }),
}
