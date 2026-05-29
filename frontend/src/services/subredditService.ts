import type { MessageResponse, Post, Subreddit, SubredditRecommendation } from '../types'
import { apiRequest } from './api'

export const subredditService = {
  getAll: () => apiRequest<Subreddit[]>('/subreddits/'),
  getById: (id: number) => apiRequest<Subreddit>(`/subreddits/${id}`),
  getPosts: (id: number, limit = 25) => apiRequest<Post[]>(`/subreddits/${id}/posts`, { query: { limit } }),
  create: (userId: number, name: string, description: string) =>
    apiRequest<Subreddit>('/subreddits/', { method: 'POST', userId, body: { name, description } }),
  subscribe: (userId: number, subredditId: number) =>
    apiRequest<MessageResponse>(`/subreddits/${subredditId}/subscribe`, { method: 'POST', userId }),
  unsubscribe: (userId: number, subredditId: number) =>
    apiRequest<MessageResponse>(`/subreddits/${subredditId}/subscribe`, { method: 'DELETE', userId }),
  recommendations: (userId: number, limit = 10) =>
    apiRequest<SubredditRecommendation[]>('/subreddits/recommendations', { userId, query: { limit } }),
}
