import { useEffect, useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { ArrowLeftIcon, TrophyIcon, ChatBubbleLeftIcon, UserGroupIcon } from '@heroicons/react/24/outline'
import { userService } from '../services/userService'
import { postService } from '../services/postService'
import { memberSince } from '../utils/time'
import PostCard from '../components/PostCard'
import type { Post, Redditor } from '../types'
import { useAuth } from '../context/AuthContext'
import { useData } from '../context/DataContext'

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

type Tab = 'posts' | 'communities'

export default function UserProfilePage() {
  const { username } = useParams<{ username: string }>()
  const navigate = useNavigate()
  const { currentUser } = useAuth()
  const { subreddits, subscribedIds, unsubscribe } = useData()
  const [user, setUser] = useState<Redditor | null>(null)
  const [userPosts, setUserPosts] = useState<Post[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [tab, setTab] = useState<Tab>('posts')
  const [unjoining, setUnjoining] = useState<number | null>(null)

  const isOwnProfile = currentUser?.username === username

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

  async function handleUnjoin(subredditId: number) {
    setUnjoining(subredditId)
    try {
      await unsubscribe(subredditId)
    } finally {
      setUnjoining(null)
    }
  }

  if (loading) return (
    <div className="text-[#818384] py-6">Loading user...</div>
  )

  if (!user) return (
    <div className="text-[#818384] py-6">User not found.</div>
  )

  const gradient = AVATAR_GRADIENTS[user.user_id % AVATAR_GRADIENTS.length]
  const joinedCommunities = subreddits.filter(s => subscribedIds.has(s.subreddit_id))

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
            {isOwnProfile && (
              <div className="flex items-center gap-2">
                <UserGroupIcon className="w-4 h-4 text-green-400" />
                <div>
                  <p className="text-sm font-bold text-white">{joinedCommunities.length}</p>
                  <p className="text-[10px] text-[#818384]">Communities</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Tabs — only show Communities tab for own profile */}
      <div className="flex border-b border-[#343536]">
        <button
          onClick={() => setTab('posts')}
          className={`px-4 py-2 text-sm font-medium transition-colors ${
            tab === 'posts'
              ? 'text-white border-b-2 border-orange-500'
              : 'text-[#818384] hover:text-white'
          }`}
        >
          Posts
        </button>
        {isOwnProfile && (
          <button
            onClick={() => setTab('communities')}
            className={`px-4 py-2 text-sm font-medium transition-colors ${
              tab === 'communities'
                ? 'text-white border-b-2 border-orange-500'
                : 'text-[#818384] hover:text-white'
            }`}
          >
            Communities
          </button>
        )}
      </div>

      {tab === 'posts' && (
        <div>
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
      )}

      {tab === 'communities' && isOwnProfile && (
        <div className="flex flex-col gap-2">
          {joinedCommunities.length === 0 ? (
            <div className="bg-[#1a1a1b] border border-[#343536] rounded-md p-8 text-center text-[#818384] text-sm">
              Not joined any communities yet.
            </div>
          ) : (
            joinedCommunities.map(sub => (
              <div
                key={sub.subreddit_id}
                className="flex items-center justify-between bg-[#1a1a1b] border border-[#343536] rounded-md px-4 py-3"
              >
                <div className="flex flex-col min-w-0">
                  <Link
                    to={`/r/${sub.name}`}
                    className="text-sm font-semibold text-white hover:underline"
                  >
                    r/{sub.name}
                  </Link>
                  <p className="text-[11px] text-[#818384] mt-0.5">
                    {sub.subscriber_count.toLocaleString()} members
                  </p>
                </div>
                <button
                  onClick={() => handleUnjoin(sub.subreddit_id)}
                  disabled={unjoining === sub.subreddit_id}
                  className="ml-4 shrink-0 px-3 py-1 text-xs font-medium rounded-full border border-[#343536] text-[#818384] hover:border-red-500 hover:text-red-400 transition-colors disabled:opacity-40"
                >
                  {unjoining === sub.subreddit_id ? 'Leaving…' : 'Leave'}
                </button>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  )
}
