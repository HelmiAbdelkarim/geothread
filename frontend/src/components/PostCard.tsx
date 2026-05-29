import { useState } from 'react'
import { Link } from 'react-router-dom'
import { ArrowUpIcon, ArrowDownIcon, ChatBubbleLeftIcon, ShareIcon, PhotoIcon, MapPinIcon } from '@heroicons/react/24/outline'
import { ArrowUpIcon as ArrowUpSolid, ArrowDownIcon as ArrowDownSolid } from '@heroicons/react/24/solid'
import type { Post } from '../types'
import { useData } from '../context/DataContext'
import { formatDistance } from '../utils/geo'
import { timeAgo } from '../utils/time'

interface Props {
  post: Post
  onClick?: () => void
  distanceKm?: number
}

export default function PostCard({ post, onClick, distanceKm }: Props) {
  const { userById, subredditById, votePost } = useData()
  const [pendingVote, setPendingVote] = useState(false)
  const author = userById.get(post.author_id)
  const subreddit = subredditById.get(post.subreddit_id)
  const vote = (post.user_vote ?? 0) as 1 | -1 | 0
  const score = post.score ?? post.upvotes - post.downvotes
  const subredditName = post.subreddit_name ?? subreddit?.name
  const authorName = post.author_username ?? author?.username
  const subredditSlug = subredditName ?? ''

  async function handleVote(nextVote: 1 | -1) {
    if (pendingVote) return
    setPendingVote(true)
    try {
      await votePost(post.post_id, vote === nextVote ? 'remove' : nextVote === 1 ? 'up' : 'down')
    } finally {
      setPendingVote(false)
    }
  }

  return (
    <div
      className="flex bg-white border border-gray-200 rounded hover:border-gray-400 cursor-pointer overflow-hidden"
      onClick={onClick}
    >
      {/* Vote column */}
      <div className="flex flex-col items-center gap-1 px-2 py-2 bg-gray-50 w-10 shrink-0">
        <button
          onClick={e => { e.stopPropagation(); handleVote(1) }}
          disabled={pendingVote}
          className={vote === 1 ? 'text-orange-500' : 'text-gray-400 hover:text-orange-500'}
        >
          {vote === 1 ? <ArrowUpSolid className="w-4 h-4" /> : <ArrowUpIcon className="w-4 h-4" />}
        </button>
        <span className={`text-xs font-bold ${vote === 1 ? 'text-orange-500' : vote === -1 ? 'text-blue-500' : 'text-gray-700'}`}>
          {score >= 1000 ? `${(score / 1000).toFixed(1)}k` : score}
        </span>
        <button
          onClick={e => { e.stopPropagation(); handleVote(-1) }}
          disabled={pendingVote}
          className={vote === -1 ? 'text-blue-500' : 'text-gray-400 hover:text-blue-500'}
        >
          {vote === -1 ? <ArrowDownSolid className="w-4 h-4" /> : <ArrowDownIcon className="w-4 h-4" />}
        </button>
      </div>

      {/* Content */}
      <div className="flex flex-1 min-w-0 justify-between gap-3 px-3 py-2">
        <div className="flex flex-col gap-1 min-w-0">
          <div className="flex items-center gap-1 text-xs text-gray-500 flex-wrap">
            <Link
              to={`/r/${subredditSlug}`}
              onClick={e => e.stopPropagation()}
              className="font-semibold text-gray-800 hover:underline"
            >
              r/{subredditName ?? 'unknown'}
            </Link>
            <span>•</span>
            <span>
              Posted by{' '}
              <Link
                to={`/u/${authorName ?? ''}`}
                onClick={e => e.stopPropagation()}
                className="hover:underline"
              >
                u/{authorName ?? 'unknown'}
              </Link>
            </span>
            <span>•</span>
            <span>{timeAgo(post.timestamp)}</span>
            {distanceKm != null && (
              <>
                <span>•</span>
                <span className="flex items-center gap-0.5 text-orange-500 font-medium">
                  <MapPinIcon className="w-3 h-3" />
                  {formatDistance(distanceKm)}
                </span>
              </>
            )}
          </div>
          <h2 className="text-sm font-medium text-gray-900 leading-snug">{post.title}</h2>
          {!post.image_url && (
            <p className="text-xs text-gray-500 line-clamp-2">{post.content}</p>
          )}
          <div className="flex items-center gap-3 text-xs text-gray-500 mt-1">
            <span className="flex items-center gap-1">
              <ChatBubbleLeftIcon className="w-3.5 h-3.5" />
              {post.comments} comments
            </span>
            <span className="flex items-center gap-1">
              <ShareIcon className="w-3.5 h-3.5" />
              Share
            </span>
          </div>
        </div>

        {post.image_url ? (
          <img src={post.image_url} alt="" className="w-20 h-16 object-cover rounded shrink-0 self-center" />
        ) : (
          <div className="w-20 h-16 bg-gray-100 rounded shrink-0 self-center flex items-center justify-center">
            <PhotoIcon className="w-6 h-6 text-gray-300" />
          </div>
        )}
      </div>
    </div>
  )
}
