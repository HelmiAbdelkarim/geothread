import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeftIcon, UserGroupIcon } from '@heroicons/react/24/outline'
import { ShieldCheckIcon } from '@heroicons/react/24/solid'
import { FireIcon, SparklesIcon, ChartBarIcon, ArrowTrendingUpIcon, BoltIcon } from '@heroicons/react/24/outline'
import { useData } from '../context/DataContext'
import { postService } from '../services/postService'
import { sortPosts } from '../utils/ranking'
import type { Post, SortStrategy } from '../types'
import PostCard from '../components/PostCard'

const PAGE_SIZE = 5

const SORTS: { key: SortStrategy; label: string; icon: React.ReactNode }[] = [
  { key: 'hot',           label: 'Hot',           icon: <FireIcon className="w-4 h-4" /> },
  { key: 'new',           label: 'New',           icon: <SparklesIcon className="w-4 h-4" /> },
  { key: 'top',           label: 'Top',           icon: <ChartBarIcon className="w-4 h-4" /> },
  { key: 'rising',        label: 'Rising',        icon: <ArrowTrendingUpIcon className="w-4 h-4" /> },
  { key: 'controversial', label: 'Controversial', icon: <BoltIcon className="w-4 h-4" /> },
]

const GRADIENT_PAIRS = [
  'from-orange-500 to-red-600',
  'from-blue-500 to-indigo-600',
  'from-green-500 to-teal-600',
  'from-purple-500 to-pink-600',
  'from-yellow-500 to-orange-600',
]

function formatCount(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`
  return String(n)
}

export default function SubredditPage() {
  const { subredditName } = useParams<{ subredditName: string }>()
  const { subreddits, subscribe, unsubscribe } = useData()
  const navigate = useNavigate()
  const [joined, setJoined] = useState(false)
  const [sort, setSort] = useState<SortStrategy>('hot')
  const [visible, setVisible] = useState(PAGE_SIZE)
  const [posts, setPosts] = useState<Post[]>([])
  const [loadingPosts, setLoadingPosts] = useState(false)
  const [error, setError] = useState('')

  const subreddit = subreddits.find(s => s.name.toLowerCase() === (subredditName ?? '').toLowerCase())

  useEffect(() => {
    if (!subreddit) return
    let ignore = false
    setLoadingPosts(true)
    postService.getBySubreddit(subreddit.subreddit_id, 100)
      .then(nextPosts => { if (!ignore) setPosts(nextPosts) })
      .catch(err => { if (!ignore) setError(err instanceof Error ? err.message : 'Failed to load community posts.') })
      .finally(() => { if (!ignore) setLoadingPosts(false) })
    return () => { ignore = true }
  }, [subreddit])

  async function toggleJoined() {
    if (!subreddit) return
    try {
      if (joined) {
        await unsubscribe(subreddit.subreddit_id)
        setJoined(false)
      } else {
        await subscribe(subreddit.subreddit_id)
        setJoined(true)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update subscription.')
    }
  }

  if (!subreddit) return (
    <div className="text-[#818384] py-6">Community not found.</div>
  )

  const subredditPosts = posts.filter(p => p.subreddit_id === subreddit.subreddit_id)
  const sorted = sortPosts(subredditPosts, sort)
  const shown = sorted.slice(0, visible)
  const hasMore = visible < sorted.length
  const gradient = GRADIENT_PAIRS[subreddit.subreddit_id % GRADIENT_PAIRS.length]

  return (
    <div className="flex flex-col">
      <button
        onClick={() => navigate(-1)}
        className="flex items-center gap-1 text-sm text-[#818384] hover:text-white mb-4 transition-colors"
      >
        <ArrowLeftIcon className="w-4 h-4" />
        Back
      </button>

      <div className="bg-[#1a1a1b] border border-[#343536] rounded-md overflow-hidden mb-4">
        <div className={`h-20 bg-gradient-to-r ${gradient}`} />
        <div className="px-4 pb-4 pt-3 flex items-end gap-4">
          <div className={`w-14 h-14 rounded-full bg-gradient-to-br ${gradient} border-4 border-[#1a1a1b] -mt-7 shrink-0`} />
          <div className="flex-1 min-w-0">
            <h1 className="text-xl font-bold text-white">r/{subreddit.name}</h1>
            <p className="text-xs text-[#818384] mt-0.5">{subreddit.description}</p>
          </div>
          <button
            onClick={toggleJoined}
            className={`shrink-0 px-5 py-1.5 rounded-full text-sm font-semibold transition-colors ${
              joined
                ? 'border border-[#818384] text-[#d7dadc] hover:border-white'
                : 'bg-orange-500 hover:bg-orange-600 text-white'
            }`}
          >
            {joined ? 'Joined' : 'Join'}
          </button>
        </div>
        <div className="px-4 pb-4 flex gap-6">
          <div className="flex items-center gap-1.5 text-xs text-[#818384]">
            <UserGroupIcon className="w-4 h-4" />
            <span className="font-semibold text-white">{formatCount(subreddit.subscriber_count + (joined ? 1 : 0))}</span>
            <span>members</span>
          </div>
          <div className="flex items-center gap-1.5 text-xs text-[#818384]">
            <ShieldCheckIcon className="w-4 h-4 text-green-400" />
            <span className="font-semibold text-green-400">{Math.floor(subreddit.subscriber_count * 0.04)}</span>
            <span>online</span>
          </div>
        </div>
      </div>

      <div className="flex gap-1 bg-white border border-gray-200 rounded p-1 mb-4">
        {SORTS.map(({ key, label, icon }) => (
          <button
            key={key}
            onClick={() => { setSort(key); setVisible(PAGE_SIZE) }}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded text-sm font-medium transition-colors ${
              sort === key ? 'bg-gray-100 text-gray-900' : 'text-gray-500 hover:bg-gray-50 hover:text-gray-800'
            }`}
          >
            {icon}{label}
          </button>
        ))}
      </div>

      {error && <p className="text-sm text-red-500 mb-3">{error}</p>}

      {loadingPosts ? (
        <div className="bg-[#1a1a1b] border border-[#343536] rounded-md p-8 text-center text-[#818384] text-sm">
          Loading posts...
        </div>
      ) : shown.length === 0 ? (
        <div className="bg-[#1a1a1b] border border-[#343536] rounded-md p-8 text-center text-[#818384] text-sm">
          No posts in r/{subreddit.name} yet.
        </div>
      ) : (
        <div className="flex flex-col gap-2">
          {shown.map(post => (
            <PostCard
              key={post.post_id}
              post={post}
              onClick={() => navigate(`/post/${post.post_id}`)}
            />
          ))}
        </div>
      )}

      <div className="flex gap-3 justify-center mt-4">
        {hasMore && (
          <button
            onClick={() => setVisible(v => v + PAGE_SIZE)}
            className="px-4 py-2 text-sm font-medium text-[#d7dadc] bg-[#1a1a1b] border border-[#343536] rounded-full hover:border-[#818384] transition-colors"
          >
            Load more
          </button>
        )}
        {visible > PAGE_SIZE && (
          <button
            onClick={() => setVisible(PAGE_SIZE)}
            className="px-4 py-2 text-sm font-medium text-[#818384] hover:text-[#d7dadc] transition-colors"
          >
            Show less
          </button>
        )}
      </div>
    </div>
  )
}
