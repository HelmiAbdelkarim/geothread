import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  FireIcon, SparklesIcon, ChartBarIcon, ArrowTrendingUpIcon, BoltIcon,
  MapPinIcon, XMarkIcon,
} from '@heroicons/react/24/outline'
import type { BackendSortStrategy, SortStrategy } from '../types'
import { useData } from '../context/DataContext'
import { sortPosts } from '../utils/ranking'
import { haversine } from '../utils/geo'
import PostCard from '../components/PostCard'

const PAGE_SIZE = 5
const MOCK_USER_LAT = 48.8566
const MOCK_USER_LNG = 2.3522

const SORTS: { key: SortStrategy; label: string; icon: React.ReactNode }[] = [
  { key: 'hot',           label: 'Hot',           icon: <FireIcon className="w-4 h-4" /> },
  { key: 'new',           label: 'New',           icon: <SparklesIcon className="w-4 h-4" /> },
  { key: 'top',           label: 'Top',           icon: <ChartBarIcon className="w-4 h-4" /> },
  { key: 'rising',        label: 'Rising',        icon: <ArrowTrendingUpIcon className="w-4 h-4" /> },
  { key: 'controversial', label: 'Controversial', icon: <BoltIcon className="w-4 h-4" /> },
  { key: 'closest',       label: 'Closest',       icon: <MapPinIcon className="w-4 h-4" /> },
]

export default function FeedPage() {
  const { posts, loading, error, sort: backendSort, setSort: setBackendSort } = useData()
  const navigate = useNavigate()
  const [sort, setSort] = useState<SortStrategy>(backendSort)
  const [visible, setVisible] = useState(PAGE_SIZE)
  const [locationActive, setLocationActive] = useState(false)
  const [radius, setRadius] = useState(25)

  const userLat = locationActive ? MOCK_USER_LAT : undefined
  const userLng = locationActive ? MOCK_USER_LNG : undefined

  function postDistance(p: typeof posts[0]): number | null {
    if (!locationActive || p.lat == null || p.lng == null) return null
    return haversine(MOCK_USER_LAT, MOCK_USER_LNG, p.lat, p.lng)
  }

  const withinRadius = (p: typeof posts[0]) => {
    const d = postDistance(p)
    return !locationActive || d === null || d <= radius
  }

  function handleSortChange(s: SortStrategy) {
    setSort(s)
    setVisible(PAGE_SIZE)
    if (s !== 'closest') setBackendSort(s as BackendSortStrategy)
    if (s === 'closest' && !locationActive) setLocationActive(true)
  }

  const filtered = posts.filter(withinRadius)
  const sorted = sortPosts(filtered, sort, userLat, userLng)
  const shown = sorted.slice(0, visible)
  const hasMore = visible < sorted.length

  return (
    <div className="flex flex-col gap-3">
      {!locationActive && (
        <div className="flex items-center justify-between bg-[#1a1a1b] border border-[#343536] rounded-md px-4 py-3">
          <div className="flex items-center gap-2 text-sm text-[#d7dadc]">
            <MapPinIcon className="w-4 h-4 text-orange-400 shrink-0" />
            Enable location to see nearby posts and sort by distance
          </div>
          <button
            onClick={() => setLocationActive(true)}
            className="shrink-0 ml-4 px-3 py-1 text-xs font-semibold rounded-full bg-orange-500 hover:bg-orange-600 text-white transition-colors"
          >
            Enable
          </button>
        </div>
      )}

      {locationActive && (
        <div className="bg-[#1a1a1b] border border-[#343536] rounded-md px-4 py-3 flex items-center gap-4">
          <MapPinIcon className="w-4 h-4 text-orange-400 shrink-0" />
          <span className="text-xs text-[#818384] shrink-0">Radius</span>
          <input
            type="range" min={5} max={100} step={5} value={radius}
            onChange={e => { setRadius(Number(e.target.value)); setVisible(PAGE_SIZE) }}
            className="flex-1 accent-orange-500"
          />
          <span className="text-xs font-semibold text-white w-14 shrink-0">{radius} km</span>
          <button
            onClick={() => { setLocationActive(false); if (sort === 'closest') setSort('hot') }}
            className="text-[#818384] hover:text-white transition-colors"
          >
            <XMarkIcon className="w-4 h-4" />
          </button>
        </div>
      )}

      <div className="flex gap-1 bg-white border border-gray-200 rounded p-1">
        {SORTS.map(({ key, label, icon }) => (
          <button
            key={key}
            onClick={() => handleSortChange(key)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded text-sm font-medium transition-colors ${
              sort === key ? 'bg-gray-100 text-gray-900' : 'text-gray-500 hover:bg-gray-50 hover:text-gray-800'
            }`}
          >
            {icon}{label}
          </button>
        ))}
      </div>

      <div className="flex flex-col gap-2">
        {loading && <p className="text-sm text-[#818384] text-center py-8">Loading backend feed...</p>}
        {error && <p className="text-sm text-red-500 text-center py-8">{error}</p>}
        {shown.map(post => (
          <PostCard
            key={post.post_id}
            post={post}
            onClick={() => navigate(`/post/${post.post_id}`)}
            distanceKm={postDistance(post) ?? undefined}
          />
        ))}
        {!loading && shown.length === 0 && (
          <p className="text-sm text-[#818384] text-center py-8">
            No posts within {radius} km. Try increasing the radius.
          </p>
        )}
      </div>

      <div className="flex gap-3 justify-center mt-1">
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
