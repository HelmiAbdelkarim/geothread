import { useCallback, useEffect, useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import {
  ArrowUpIcon, ArrowDownIcon,
  ChatBubbleLeftIcon, ShareIcon, BookmarkIcon, ArrowLeftIcon,
} from '@heroicons/react/24/outline'
import { ArrowUpIcon as ArrowUpSolid, ArrowDownIcon as ArrowDownSolid } from '@heroicons/react/24/solid'
import type { Comment } from '../types'
import { useData } from '../context/DataContext'
import { commentService } from '../services/commentService'
import { postService } from '../services/postService'
import { useAuth } from '../context/AuthContext'
import { timeAgo } from '../utils/time'
import CommentItem from '../components/CommentItem'

export default function PostDetailPage() {
  const { postId } = useParams<{ postId: string }>()
  const { posts, userById, subredditById, votePost, refreshFeed } = useData()
  const { currentUser } = useAuth()
  const navigate = useNavigate()

  const [post, setPost] = useState(() => posts.find(p => p.post_id === Number(postId)) ?? null)
  const [localComments, setLocalComments] = useState<Comment[]>([])
  const [newText, setNewText] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [pendingVote, setPendingVote] = useState(false)

  const loadPost = useCallback(async () => {
    const id = Number(postId)
    if (!id) return
    setLoading(true)
    try {
      const [nextPost, thread] = await Promise.all([
        postService.getById(id, currentUser?.user_id),
        commentService.getByPost(id, currentUser?.user_id),
      ])
      setPost(nextPost)
      setLocalComments(thread.comments)
      setError('')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load post.')
    } finally {
      setLoading(false)
    }
  }, [currentUser, postId])

  useEffect(() => {
    loadPost()
  }, [loadPost])

  async function handleVote(nextVote: 1 | -1) {
    if (!post || pendingVote) return
    setPendingVote(true)
    try {
      const currentVote = (post.user_vote ?? 0) as 1 | -1 | 0
      await votePost(post.post_id, currentVote === nextVote ? 'remove' : nextVote === 1 ? 'up' : 'down')
      const nextPost = await postService.getById(post.post_id, currentUser?.user_id)
      setPost(nextPost)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to vote.')
    } finally {
      setPendingVote(false)
    }
  }

  if (loading && !post) return (
    <div className="max-w-3xl mx-auto px-4 py-6 text-[#818384]">Loading post...</div>
  )

  if (!post) return (
    <div className="max-w-3xl mx-auto px-4 py-6 text-[#818384]">Post not found.</div>
  )

  const author = userById.get(post.author_id)
  const subreddit = subredditById.get(post.subreddit_id)
  const subredditName = post.subreddit_name ?? subreddit?.name
  const authorName = post.author_username ?? author?.username
  const subredditSlug = subredditName ?? ''
  const score = post.score ?? post.upvotes - post.downvotes
  const vote = (post.user_vote ?? 0) as 1 | -1 | 0

  async function submitTopLevel() {
    if (!newText.trim() || !currentUser || !post) return
    try {
      await commentService.create(currentUser.user_id, post.post_id, newText.trim())
      setNewText('')
      await loadPost()
      await refreshFeed()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to comment.')
    }
  }

  async function addReply(parentId: number, content: string) {
    if (!currentUser || !post) return
    try {
      await commentService.create(currentUser.user_id, post.post_id, content, parentId)
      await loadPost()
      await refreshFeed()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to reply.')
    }
  }

  return (
    <div className="flex flex-col">
      <button
        onClick={() => navigate(-1)}
        className="flex items-center gap-1 text-sm text-[#818384] hover:text-white mb-4 transition-colors"
      >
        <ArrowLeftIcon className="w-4 h-4" />
        Back
      </button>

      {error && <p className="text-sm text-red-500 mb-3">{error}</p>}

      <div className="bg-[#1a1a1b] border border-[#343536] rounded-md overflow-hidden mb-4">
        {post.image_url && (
          <img src={post.image_url} alt="" className="w-full max-h-[512px] object-cover" />
        )}
        <div className="flex gap-3 p-4">
          <div className="flex flex-col items-center gap-1 shrink-0">
            <button
              onClick={() => handleVote(1)}
              disabled={pendingVote}
              className={vote === 1 ? 'text-orange-500' : 'text-[#818384] hover:text-orange-500'}
            >
              {vote === 1 ? <ArrowUpSolid className="w-5 h-5" /> : <ArrowUpIcon className="w-5 h-5" />}
            </button>
            <span className={`text-sm font-bold ${vote === 1 ? 'text-orange-500' : vote === -1 ? 'text-blue-400' : 'text-white'}`}>
              {score >= 1000 ? `${(score / 1000).toFixed(1)}k` : score}
            </span>
            <button
              onClick={() => handleVote(-1)}
              disabled={pendingVote}
              className={vote === -1 ? 'text-blue-400' : 'text-[#818384] hover:text-blue-400'}
            >
              {vote === -1 ? <ArrowDownSolid className="w-5 h-5" /> : <ArrowDownIcon className="w-5 h-5" />}
            </button>
          </div>

          <div className="flex flex-col gap-2 min-w-0">
            <div className="flex items-center gap-1 text-xs text-[#818384]">
              <Link to={`/r/${subredditSlug}`} className="font-semibold text-white hover:underline">
                r/{subredditName ?? 'unknown'}
              </Link>
              <span>•</span>
              <span>
                Posted by{' '}
                <Link to={`/u/${authorName ?? ''}`} className="hover:underline">
                  u/{authorName ?? 'unknown'}
                </Link>
              </span>
              <span>•</span>
              <span>{timeAgo(post.timestamp)}</span>
            </div>
            <h1 className="text-lg font-semibold text-white leading-snug">{post.title}</h1>
            <p className="text-sm text-[#d7dadc] leading-relaxed">{post.content}</p>

            <div className="flex items-center gap-1 mt-2 text-[#818384]">
              <button className="flex items-center gap-1.5 px-2 py-1.5 rounded hover:bg-[#272729] text-xs font-medium transition-colors">
                <ChatBubbleLeftIcon className="w-4 h-4" />
                {post.comments} Comments
              </button>
              <button className="flex items-center gap-1.5 px-2 py-1.5 rounded hover:bg-[#272729] text-xs font-medium transition-colors">
                <ShareIcon className="w-4 h-4" />
                Share
              </button>
              <button className="flex items-center gap-1.5 px-2 py-1.5 rounded hover:bg-[#272729] text-xs font-medium transition-colors">
                <BookmarkIcon className="w-4 h-4" />
                Save
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-[#1a1a1b] border border-[#343536] rounded-md p-4 mb-3">
        <p className="text-xs text-[#818384] mb-2">
          Comment as <span className="text-white font-medium">u/{currentUser?.username ?? 'guest'}</span>
        </p>
        <textarea
          value={newText}
          onChange={e => setNewText(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) submitTopLevel() }}
          placeholder="What are your thoughts?"
          rows={4}
          className="w-full bg-[#272729] border border-[#343536] focus:border-[#818384] rounded text-sm text-[#d7dadc] placeholder-[#818384] p-3 outline-none resize-none transition-colors"
        />
        <div className="flex justify-end mt-2">
          <button
            onClick={submitTopLevel}
            disabled={!newText.trim() || !currentUser}
            className="px-4 py-1.5 text-sm font-semibold rounded-full bg-orange-500 hover:bg-orange-600 text-white disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            Comment
          </button>
        </div>
      </div>

      <div className="bg-[#1a1a1b] border border-[#343536] rounded-md p-4">
        <p className="text-xs text-[#818384] mb-4">
          {localComments.length} comment{localComments.length !== 1 ? 's' : ''}
        </p>
        <div className="flex flex-col gap-3">
          {localComments.length === 0 ? (
            <p className="text-sm text-[#818384]">No comments yet.</p>
          ) : (
            localComments.map(comment => (
              <CommentItem key={comment.comment_id ?? comment.id} comment={comment} onReply={addReply} onChanged={loadPost} />
            ))
          )}
        </div>
      </div>
    </div>
  )
}
