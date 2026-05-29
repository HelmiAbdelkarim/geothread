import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  FireIcon, SparklesIcon, ChartBarIcon, ArrowTrendingUpIcon, BoltIcon,
  MapPinIcon, XMarkIcon,
} from '@heroicons/react/24/outline'
import type { BackendSortStrategy, SortStrategy } from '../types'
import { useData } from '../context/DataContext'
import { useAuth } from '../context/AuthContext'
import { sortPosts } from '../utils/ranking'
import { haversine } from '../utils/geo'
import { userService } from '../services/userService'
import PostCard from '../components/PostCard'

const PAGE_SIZE = 5

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
  const { currentUser } = useAuth()
  const navigate = useNavigate()
  const [sort, setSort] = useState<SortStrategy>(backendSort)
  const [visible, setVisible] = useState(PAGE_SIZE)
  const [locationActive, setLocationActive] = useState(false)
  const [locationLoading, setLocationLoading] = useState(false)
  const [locationError, setLocationError] = useState<string | null>(null)
  const [userLat, setUserLat] = useState<number | null>(null)
  const [userLng, setUserLng] = useState<number | null>(null)
  const [radius, setRadius] = useState(25)

  function enableLocation() {
    if (!navigator.geolocation) {
      setLocationError('Geolocation is not supported by your browser.')
      return
    }
    setLocationLoading(true)
    setLocationError(null)
    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        const lat = pos.coords.latitude
        const lng = pos.coords.longitude
        setUserLat(lat)
        setUserLng(lng)
        setLocationActive(true)
        setLocationLoading(false)
        if (currentUser) {
          try {
            await userService.updateLocation(currentUser.user_id, { latitude: lat, longitude: lng })
          } catch {
            // non-fatal — location display still works
          }
        }
      },
      (err) => {
        setLocationError(err.message)
        setLocationLoading(false)
      },
      { enableHighAccuracy: false, timeout: 8000 },
    )
  }

  function disableLocation() {
    setLocationActive(false)
    setUserLat(null)
    setUserLng(null)
    setLocationError(null)
    if (sort === 'closest') setSort('hot')
  }

  function postDistance(p: typeof posts[0]): number | null {
    if (!locationActive || userLat == null || userLng == null) return null
    if (p.latitude == null || p.longitude == null) return null
    return haversine(userLat, userLng, p.latitude, p.longitude)
  }

  const withinRadius = (p: typeof posts[0]) => {
    const d = postDistance(p)
    return !locationActive || d === null || d <= radius
  }

  function handleSortChange(s: SortStrategy) {
    setSort(s)
    setVisible(PAGE_SIZE)
    if (s !== 'closest') setBackendSort(s as BackendSortStrategy)
    if (s === 'closest' && !locationActive) enableLocation()
  }

  const filtered = posts.filter(withinRadius)
  const sorted = sortPosts(filtered, sort, userLat ?? undefined, userLng ?? undefined)
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
            onClick={enableLocation}
            disabled={locationLoading}
            className="shrink-0 ml-4 px-3 py-1 text-xs font-semibold rounded-full bg-orange-500 hover:bg-orange-600 text-white transition-colors disabled:opacity-50"
          >
            {locationLoading ? 'Locating…' : 'Enable'}
          </button>
        </div>
      )}

      {locationError && (
        <p className="text-xs text-red-400 px-1">{locationError}</p>
      )}

      {locationActive && userLat != null && (
        <div className="bg-[#1a1a1b] border border-[#343536] rounded-md px-4 py-3 flex items-center gap-4">
          <MapPinIcon className="w-4 h-4 text-orange-400 shrink-0" />
          <span className="text-xs text-orange-300 shrink-0">
            {userLat.toFixed(4)}, {userLng?.toFixed(4)}
          </span>
          <span className="text-xs text-[#818384] shrink-0">Radius</span>
          <input
            type="range" min={5} max={100} step={5} value={radius}
            onChange={e => { setRadius(Number(e.target.value)); setVisible(PAGE_SIZE) }}
            className="flex-1 accent-orange-500"
          />
          <span className="text-xs font-semibold text-white w-14 shrink-0">{radius} km</span>
          <button onClick={disableLocation} className="text-[#818384] hover:text-white transition-colors">
            <XMarkIcon className="w-4 h-4" />
          </button>
        </div>
      )}

      <div className="flex gap-1 bg-[#1a1a1b] border border-[#343536] rounded p-1">
        {SORTS.map(({ key, label, icon }) => (
          <button
            key={key}
            onClick={() => handleSortChange(key)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded text-sm font-medium transition-colors ${
              sort === key ? 'bg-[#272729] text-white' : 'text-[#818384] hover:bg-[#272729] hover:text-[#d7dadc]'
            }`}
          >
            {icon}{label}
          </button>
        ))}
      </div>

      <div className="flex flex-col gap-2">
        {loading && <p className="text-sm text-[#818384] text-center py-8">Loading backend feed…</p>}
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
            {locationActive
              ? `No posts within ${radius} km. Try increasing the radius.`
              : 'No posts in your feed. Join some communities!'}
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
