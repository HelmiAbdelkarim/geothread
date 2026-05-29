import type { Redditor, UserStats } from '../types'
import { apiRequest } from './api'

export const userService = {
  getAll: (limit = 50) => apiRequest<Redditor[]>('/users/', { query: { limit } }),
  getMe: (userId: number) => apiRequest<Redditor>('/users/me', { userId }),
  getStats: (userId: number) => apiRequest<UserStats>('/users/me/stats', { userId }),
  getByUsername: (username: string) => apiRequest<Redditor>(`/users/${encodeURIComponent(username)}`),
  getSubscribedIds: (userId: number) => apiRequest<number[]>('/users/me/subscriptions', { userId }),
  updateLocation: (
    userId: number,
    location: { latitude: number; longitude: number; city?: string; region?: string; country?: string },
  ) => apiRequest<Redditor>('/users/me/location', { method: 'PUT', userId, body: location }),
}
