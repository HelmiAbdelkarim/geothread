import type { BackendSortStrategy, MessageResponse, Post, VoteDirection } from '../types'
import { apiRequest } from './api'

export const postService = {
  getFeed: (userId: number | null | undefined, sort: BackendSortStrategy = 'hot', limit = 25) =>
    apiRequest<Post[]>('/posts/', { userId, query: { sort, limit } }),
  getById: (id: number, userId?: number | null) => apiRequest<Post>(`/posts/${id}`, { userId }),
  getBySubreddit: (subredditId: number, limit = 25) =>
    apiRequest<Post[]>(`/subreddits/${subredditId}/posts`, { query: { limit } }),
  getByUser: (userId: number) => apiRequest<Post[]>(`/posts/user/${userId}`),
  create: (
    userId: number,
    subredditId: number,
    title: string,
    content: string,
    latitude?: number,
    longitude?: number,
    locationName?: string,
  ) =>
    apiRequest<Post>('/posts/', {
      method: 'POST',
      userId,
      body: { subreddit_id: subredditId, title, content, latitude, longitude, location_name: locationName },
    }),
  vote: (userId: number, postId: number, direction: VoteDirection) =>
    apiRequest<MessageResponse>(`/posts/${postId}/vote`, {
      method: 'POST',
      userId,
      body: { direction },
    }),
}
