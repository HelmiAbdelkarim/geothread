import type { Comment, CommentTree, MessageResponse, VoteDirection } from '../types'
import { apiRequest } from './api'

export const commentService = {
  getByPost: (postId: number, userId?: number | null, sort: 'score' | 'time' = 'score') =>
    apiRequest<CommentTree>(`/comments/post/${postId}`, { userId, query: { sort } }),
  getByUser: (userId: number) => apiRequest<Comment[]>(`/comments/user/${userId}`),
  create: (userId: number, postId: number, content: string, parentCommentId?: number | null) =>
    apiRequest<Comment>('/comments/', {
      method: 'POST',
      userId,
      body: { post_id: postId, content, parent_comment_id: parentCommentId ?? null },
    }),
  edit: (userId: number, commentId: number, content: string) =>
    apiRequest<Comment>(`/comments/${commentId}`, { method: 'PUT', userId, body: { content } }),
  delete: (userId: number, commentId: number) =>
    apiRequest<MessageResponse>(`/comments/${commentId}`, { method: 'DELETE', userId }),
  vote: (userId: number, commentId: number, direction: VoteDirection) =>
    apiRequest<MessageResponse>(`/comments/${commentId}/vote`, {
      method: 'POST',
      userId,
      query: { direction },
    }),
}
