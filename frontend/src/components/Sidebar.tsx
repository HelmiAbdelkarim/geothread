import { Link } from 'react-router-dom'
import { UserGroupIcon, PlusIcon, FireIcon, GlobeAltIcon } from '@heroicons/react/24/outline'
import { ShieldCheckIcon } from '@heroicons/react/24/solid'
import { useData } from '../context/DataContext'

interface Props {
  onCreatePost: () => void
  onCreateCommunity: () => void
}

function formatCount(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`
  return String(n)
}

const RULES = [
  'Be respectful and civil',
  'No spam or self-promotion',
  'Stay on topic',
  'No misinformation',
  'Credit original sources',
]

export default function Sidebar({ onCreatePost, onCreateCommunity }: Props) {
  const { subreddits, recommendations, stats, subscribe } = useData()
  const topCommunities = [...subreddits].sort((a, b) => b.subscriber_count - a.subscriber_count).slice(0, 8)

  return (
    <aside className="flex flex-col gap-3 w-80 shrink-0">

      <div className="bg-[#1a1a1b] border border-[#343536] rounded-md overflow-hidden">
        <div className="h-16 bg-gradient-to-br from-orange-500 to-orange-700" />
        <div className="p-3 flex flex-col gap-3">
          <div className="flex items-center gap-2">
            <GlobeAltIcon className="w-8 h-8 text-orange-500" />
            <span className="font-semibold text-white text-sm">Home</span>
          </div>
          <p className="text-xs text-[#d7dadc] leading-relaxed">
            Your personal GeoThread frontpage. Come here to check in with your favourite communities.
          </p>
          {stats && (
            <div className="grid grid-cols-3 gap-2 text-center">
              <div>
                <p className="text-sm font-bold text-white">{formatCount(stats.total_karma)}</p>
                <p className="text-[10px] text-[#818384]">karma</p>
              </div>
              <div>
                <p className="text-sm font-bold text-white">{stats.subscriptions}</p>
                <p className="text-[10px] text-[#818384]">joined</p>
              </div>
              <div>
                <p className="text-sm font-bold text-white">{stats.feed_size}</p>
                <p className="text-[10px] text-[#818384]">feed</p>
              </div>
            </div>
          )}
          <button
            onClick={onCreatePost}
            className="w-full flex items-center justify-center gap-2 bg-orange-500 hover:bg-orange-600 text-white text-sm font-semibold py-1.5 rounded-full transition-colors"
          >
            <PlusIcon className="w-4 h-4" />
            Create Post
          </button>
          <button
            onClick={onCreateCommunity}
            className="w-full flex items-center justify-center gap-2 border border-[#818384] hover:border-white text-[#d7dadc] text-sm font-semibold py-1.5 rounded-full transition-colors"
          >
            Create Community
          </button>
        </div>
      </div>

      <div className="bg-[#1a1a1b] border border-[#343536] rounded-md p-3">
        <div className="flex items-center gap-2 mb-3">
          <FireIcon className="w-4 h-4 text-orange-500" />
          <span className="text-xs font-semibold text-white uppercase tracking-wide">Top Communities</span>
        </div>
        <div className="flex flex-col">
          {topCommunities.map((sub, i) => {
            const slug = sub.name
            return (
              <Link
                key={sub.subreddit_id}
                to={`/r/${slug}`}
                className="flex items-center gap-3 py-2 px-1 rounded hover:bg-[#272729] transition-colors"
              >
                <span className="text-xs text-[#818384] w-4 shrink-0">{i + 1}</span>
                <div className="w-7 h-7 rounded-full bg-gradient-to-br from-orange-400 to-pink-500 shrink-0" />
                <div className="flex flex-col min-w-0">
                  <span className="text-xs font-medium text-white truncate">r/{sub.name}</span>
                  <div className="flex items-center gap-1 text-[10px] text-[#818384]">
                    <UserGroupIcon className="w-3 h-3" />
                    <span>{formatCount(sub.subscriber_count)} members</span>
                  </div>
                </div>
                <button
                  onClick={e => {
                    e.preventDefault()
                    subscribe(sub.subreddit_id)
                  }}
                  className="ml-auto shrink-0 text-[10px] font-semibold border border-[#818384] hover:border-white text-[#d7dadc] px-2.5 py-0.5 rounded-full transition-colors"
                >
                  Join
                </button>
              </Link>
            )
          })}
        </div>
      </div>

      {recommendations.length > 0 && (
        <div className="bg-[#1a1a1b] border border-[#343536] rounded-md p-3">
          <div className="flex items-center gap-2 mb-3">
            <GlobeAltIcon className="w-4 h-4 text-orange-500" />
            <span className="text-xs font-semibold text-white uppercase tracking-wide">Recommended Nearby</span>
          </div>
          <div className="flex flex-col gap-2">
            {recommendations.slice(0, 5).map(rec => (
              <div key={rec.subreddit_id} className="flex items-start gap-2">
                <Link to={`/r/${rec.subreddit_name}`} className="min-w-0 flex-1">
                  <p className="text-xs font-medium text-white truncate">r/{rec.subreddit_name}</p>
                  <p className="text-[10px] text-[#818384] line-clamp-2">{rec.reason}</p>
                </Link>
                <button
                  onClick={() => subscribe(rec.subreddit_id)}
                  className="shrink-0 text-[10px] font-semibold bg-orange-500 hover:bg-orange-600 text-white px-2.5 py-0.5 rounded-full transition-colors"
                >
                  Join
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="bg-[#1a1a1b] border border-[#343536] rounded-md p-3">
        <div className="flex items-center gap-2 mb-3">
          <ShieldCheckIcon className="w-4 h-4 text-orange-500" />
          <span className="text-xs font-semibold text-white uppercase tracking-wide">GeoThread Rules</span>
        </div>
        <ol className="flex flex-col gap-2">
          {RULES.map((rule, i) => (
            <li key={i} className="flex items-start gap-2 text-xs text-[#d7dadc]">
              <span className="text-[#818384] shrink-0">{i + 1}.</span>
              {rule}
            </li>
          ))}
        </ol>
      </div>

      <p className="text-[10px] text-[#818384] px-1 leading-relaxed">
        GeoThread · ASNAP Engine · ISEP 2026
      </p>
    </aside>
  )
}
