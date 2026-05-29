import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeftIcon, TrophyIcon, ChatBubbleLeftIcon } from '@heroicons/react/24/outline'
import { userService } from '../services/userService'
import { postService } from '../services/postService'
import { memberSince } from '../utils/time'
import PostCard from '../components/PostCard'
import type { Post, Redditor } from '../types'

function formatKarma(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`
  return String(n)
}

const AVATAR_GRADIENTS = [
  'from-orange-400 to-red-500',
  'from-blue-400 to-purple-500',
  'from-green-400 to-teal-500',
  'from-pink-400 to-rose-500',
  'from-yellow-400 to-orange-500',
  'from-indigo-400 to-blue-500',
]

export default function UserProfilePage() {
  const { username } = useParams<{ username: string }>()
  const navigate = useNavigate()
  const [user, setUser] = useState<Redditor | null>(null)
  const [userPosts, setUserPosts] = useState<Post[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!username) return
    let ignore = false
    setLoading(true)
    userService.getByUsername(username)
      .then(async nextUser => {
        const posts = await postService.getByUser(nextUser.user_id)
        if (!ignore) {
          setUser(nextUser)
          setUserPosts(posts)
          setError('')
        }
      })
      .catch(err => {
        if (!ignore) setError(err instanceof Error ? err.message : 'User not found.')
      })
      .finally(() => {
        if (!ignore) setLoading(false)
      })
    return () => { ignore = true }
  }, [username])

  if (loading) return (
    <div className="text-[#818384] py-6">Loading user...</div>
  )

  if (!user) return (
    <div className="text-[#818384] py-6">User not found.</div>
  )

  const gradient = AVATAR_GRADIENTS[user.user_id % AVATAR_GRADIENTS.length]

  return (
    <div className="flex flex-col gap-4">
      <button
        onClick={() => navigate(-1)}
        className="flex items-center gap-1 text-sm text-[#818384] hover:text-white transition-colors"
      >
        <ArrowLeftIcon className="w-4 h-4" />
        Back
      </button>

      {error && <p className="text-sm text-red-500">{error}</p>}

      <div className="bg-[#1a1a1b] border border-[#343536] rounded-md overflow-hidden">
        <div className={`h-20 bg-gradient-to-r ${gradient}`} />
        <div className="px-4 pb-4">
          <div className={`w-16 h-16 rounded-full bg-gradient-to-br ${gradient} border-4 border-[#1a1a1b] -mt-8 flex items-center justify-center shrink-0`}>
            <span className="text-white font-bold text-xl">{user.username[0].toUpperCase()}</span>
          </div>
          <div className="mt-2">
            <h1 className="text-xl font-bold text-white">u/{user.username}</h1>
            <p className="text-xs text-[#818384] mt-0.5">{memberSince(user.created_at)}</p>
          </div>
          <div className="flex gap-6 mt-4 pb-3 border-b border-[#343536]">
            <div className="flex items-center gap-2">
              <TrophyIcon className="w-4 h-4 text-orange-400" />
              <div>
                <p className="text-sm font-bold text-white">{formatKarma(user.post_karma)}</p>
                <p className="text-[10px] text-[#818384]">Post karma</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <ChatBubbleLeftIcon className="w-4 h-4 text-blue-400" />
              <div>
                <p className="text-sm font-bold text-white">{formatKarma(user.comment_karma)}</p>
                <p className="text-[10px] text-[#818384]">Comment karma</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div>
        <h2 className="text-sm font-semibold text-[#818384] uppercase tracking-wide mb-3">
          Posts by u/{user.username}
        </h2>
        {userPosts.length === 0 ? (
          <div className="bg-[#1a1a1b] border border-[#343536] rounded-md p-8 text-center text-[#818384] text-sm">
            No posts yet.
          </div>
        ) : (
          <div className="flex flex-col gap-2">
            {userPosts.map(post => (
              <PostCard
                key={post.post_id}
                post={post}
                onClick={() => navigate(`/post/${post.post_id}`)}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
