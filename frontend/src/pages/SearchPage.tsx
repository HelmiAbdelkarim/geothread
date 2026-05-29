import { useEffect, useState } from 'react'
import { useSearchParams, useNavigate, Link } from 'react-router-dom'
import { MagnifyingGlassIcon } from '@heroicons/react/24/outline'
import { searchService, type SearchResponse } from '../services/searchService'
import PostCard from '../components/PostCard'
import { timeAgo } from '../utils/time'

type Tab = 'all' | 'posts' | 'communities' | 'people'

export default function SearchPage() {
  const [params] = useSearchParams()
  const navigate = useNavigate()
  const q = params.get('q') ?? ''
  const [tab, setTab] = useState<Tab>('all')
  const [results, setResults] = useState<SearchResponse>({ posts: [], subreddits: [], users: [] })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!q.trim()) return
    setLoading(true)
    setError(null)
    searchService.all(q, 20)
      .then(setResults)
      .catch(err => setError(err instanceof Error ? err.message : 'Search failed'))
      .finally(() => setLoading(false))
  }, [q])

  const TABS: { key: Tab; label: string; count: number }[] = [
    { key: 'all',         label: 'All',         count: results.posts.length + results.subreddits.length + results.users.length },
    { key: 'posts',       label: 'Posts',       count: results.posts.length },
    { key: 'communities', label: 'Communities', count: results.subreddits.length },
    { key: 'people',      label: 'People',      count: results.users.length },
  ]

  const showPosts = tab === 'all' || tab === 'posts'
  const showSubs  = tab === 'all' || tab === 'communities'
  const showUsers = tab === 'all' || tab === 'people'

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center gap-2 bg-[#1a1a1b] border border-[#343536] rounded-md px-4 py-3">
        <MagnifyingGlassIcon className="w-5 h-5 text-[#818384] shrink-0" />
        <span className="text-sm text-[#d7dadc]">
          {q ? <>Results for <strong className="text-white">"{q}"</strong></> : 'Enter a search query'}
        </span>
      </div>

      <div className="flex gap-1 bg-[#1a1a1b] border border-[#343536] rounded p-1">
        {TABS.map(({ key, label, count }) => (
          <button
            key={key}
            onClick={() => setTab(key)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded text-sm font-medium transition-colors ${
              tab === key ? 'bg-[#272729] text-white' : 'text-[#818384] hover:bg-[#272729] hover:text-[#d7dadc]'
            }`}
          >
            {label}
            <span className="text-xs text-[#818384]">({count})</span>
          </button>
        ))}
      </div>

      {loading && <p className="text-sm text-[#818384] text-center py-8">Searching…</p>}
      {error   && <p className="text-sm text-red-500 text-center py-8">{error}</p>}

      {!loading && !error && (
        <div className="flex flex-col gap-4">
          {showPosts && results.posts.length > 0 && (
            <section className="flex flex-col gap-2">
              {tab === 'all' && <h3 className="text-xs font-semibold text-[#818384] uppercase tracking-wider">Posts</h3>}
              {results.posts.map(post => (
                <PostCard
                  key={post.post_id}
                  post={post}
                  onClick={() => navigate(`/post/${post.post_id}`)}
                />
              ))}
            </section>
          )}

          {showSubs && results.subreddits.length > 0 && (
            <section className="flex flex-col gap-2">
              {tab === 'all' && <h3 className="text-xs font-semibold text-[#818384] uppercase tracking-wider">Communities</h3>}
              {results.subreddits.map(sub => (
                <Link
                  key={sub.subreddit_id}
                  to={`/r/${sub.name}`}
                  className="flex items-center justify-between bg-[#1a1a1b] border border-[#343536] rounded px-4 py-3 hover:border-[#818384] transition-colors"
                >
                  <div>
                    <p className="text-sm font-semibold text-white">r/{sub.name}</p>
                    <p className="text-xs text-[#818384] line-clamp-1 mt-0.5">{sub.description}</p>
                  </div>
                  <span className="text-xs text-[#818384] shrink-0 ml-4">{sub.subscriber_count} members</span>
                </Link>
              ))}
            </section>
          )}

          {showUsers && results.users.length > 0 && (
            <section className="flex flex-col gap-2">
              {tab === 'all' && <h3 className="text-xs font-semibold text-[#818384] uppercase tracking-wider">People</h3>}
              {results.users.map(user => (
                <Link
                  key={user.user_id}
                  to={`/u/${user.username}`}
                  className="flex items-center justify-between bg-[#1a1a1b] border border-[#343536] rounded px-4 py-3 hover:border-[#818384] transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-orange-400 to-pink-500 flex items-center justify-center text-white text-xs font-bold shrink-0">
                      {user.username.slice(0, 2).toUpperCase()}
                    </div>
                    <div>
                      <p className="text-sm font-semibold text-white">u/{user.username}</p>
                      <p className="text-xs text-[#818384]">Joined {timeAgo(user.created_at)}</p>
                    </div>
                  </div>
                  <span className="text-xs text-[#818384] shrink-0 ml-4">{user.total_karma ?? user.post_karma + user.comment_karma} karma</span>
                </Link>
              ))}
            </section>
          )}

          {!loading && q && results.posts.length === 0 && results.subreddits.length === 0 && results.users.length === 0 && (
            <p className="text-sm text-[#818384] text-center py-8">No results found for "{q}".</p>
          )}
        </div>
      )}
    </div>
  )
}
