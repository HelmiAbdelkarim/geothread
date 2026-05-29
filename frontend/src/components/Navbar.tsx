import { useState, useRef, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import {
  MagnifyingGlassIcon,
  PlusIcon,
  UserIcon,
  ArrowLeftStartOnRectangleIcon,
} from '@heroicons/react/24/outline'
import { UserCircleIcon } from '@heroicons/react/24/solid'
import { useAuth } from '../context/AuthContext'

interface Props {
  onCreatePost: () => void
  onShowLogin: () => void
}

export default function Navbar({ onCreatePost, onShowLogin }: Props) {
  const { currentUser, logout } = useAuth()
  const navigate = useNavigate()
  const [showMenu, setShowMenu] = useState(false)
  const [query, setQuery] = useState('')
  const menuRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    function handler(e: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) setShowMenu(false)
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  function handleSearch(e: React.FormEvent) {
    e.preventDefault()
    const q = query.trim()
    if (!q) return
    navigate(`/search?q=${encodeURIComponent(q)}`)
  }

  const initials = currentUser?.username.slice(0, 2).toUpperCase()

  return (
    <header className="bg-[#1a1a1b] sticky top-0 z-10 border-b border-[#343536]">
      <div className="max-w-6xl mx-auto px-4 h-12 flex items-center gap-4">

        <Link to="/" className="text-white font-bold text-lg tracking-tight shrink-0 hover:text-orange-400 transition-colors">
          geothread
        </Link>

        <form onSubmit={handleSearch} className="flex-1 max-w-xl mx-auto">
          <div className="flex items-center bg-[#272729] border border-[#343536] hover:border-[#818384] focus-within:border-white rounded-full px-3 h-9 gap-2 transition-colors">
            <MagnifyingGlassIcon className="w-4 h-4 text-[#818384] shrink-0" />
            <input
              type="text"
              value={query}
              onChange={e => setQuery(e.target.value)}
              placeholder="Search GeoThread"
              className="flex-1 bg-transparent text-sm text-white placeholder-[#818384] outline-none"
            />
          </div>
        </form>

        <div className="flex items-center gap-1 shrink-0">
          <button
            onClick={onCreatePost}
            className="flex items-center gap-1 bg-[#272729] border border-[#343536] hover:border-[#818384] text-white text-sm px-3 py-1 rounded-full transition-colors"
          >
            <PlusIcon className="w-4 h-4" />
            Create
          </button>

          <div className="relative" ref={menuRef}>
            {currentUser ? (
              <button
                onClick={() => setShowMenu(o => !o)}
                className="w-8 h-8 rounded-full bg-gradient-to-br from-orange-400 to-pink-500 flex items-center justify-center text-white text-xs font-bold hover:ring-2 hover:ring-orange-400 transition-all"
              >
                {initials}
              </button>
            ) : (
              <button
                onClick={onShowLogin}
                className="text-[#818384] hover:text-white hover:bg-[#272729] p-1 rounded transition-colors"
              >
                <UserCircleIcon className="w-7 h-7" />
              </button>
            )}

            {showMenu && currentUser && (
              <div className="absolute right-0 top-10 w-52 bg-[#1a1a1b] border border-[#343536] rounded-md shadow-xl z-20 overflow-hidden">
                <div className="px-4 py-3 border-b border-[#343536]">
                  <p className="text-xs text-[#818384]">Logged in as</p>
                  <p className="text-sm font-semibold text-white">u/{currentUser.username}</p>
                </div>
                <button
                  onClick={() => { navigate(`/u/${currentUser.username}`); setShowMenu(false) }}
                  className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-[#d7dadc] hover:bg-[#272729] transition-colors"
                >
                  <UserIcon className="w-4 h-4 shrink-0" />
                  My Profile
                </button>
                <button
                  onClick={() => { logout(); setShowMenu(false) }}
                  className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-[#d7dadc] hover:bg-[#272729] transition-colors"
                >
                  <ArrowLeftStartOnRectangleIcon className="w-4 h-4 shrink-0" />
                  Log out
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  )
}
