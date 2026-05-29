import { useState, useRef, useEffect, useCallback } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import {
  MagnifyingGlassIcon,
  PlusIcon,
  UserIcon,
  ArrowLeftStartOnRectangleIcon,
  DocumentTextIcon,
  UserGroupIcon,
} from '@heroicons/react/24/outline'
import { UserCircleIcon } from '@heroicons/react/24/solid'
import { useAuth } from '../context/AuthContext'
import { searchService } from '../services/searchService'
import type { SearchResponse } from '../services/searchService'

interface Props {
  onCreatePost: () => void
  onShowLogin: () => void
}

export default function Navbar({ onCreatePost, onShowLogin }: Props) {
  const { currentUser, logout } = useAuth()
  const navigate = useNavigate()
  const [showMenu, setShowMenu] = useState(false)
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<SearchResponse | null>(null)
  const [showDrop, setShowDrop] = useState(false)
  const [searching, setSearching] = useState(false)
  const menuRef = useRef<HTMLDivElement>(null)
  const searchRef = useRef<HTMLDivElement>(null)
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  useEffect(() => {
    function handler(e: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) setShowMenu(false)
      if (searchRef.current && !searchRef.current.contains(e.target as Node)) setShowDrop(false)
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  const runSearch = useCallback(async (q: string) => {
    if (q.length < 2) { setResults(null); setShowDrop(false); return }
    setSearching(true)
    try {
      const data = await searchService.all(q, 5)
      setResults(data)
      setShowDrop(true)
    } catch {
      setResults(null)
    } finally {
      setSearching(false)
    }
  }, [])

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const q = e.target.value
    setQuery(q)
    if (debounceRef.current) clearTimeout(debounceRef.current)
    if (q.trim().length < 2) { setResults(null); setShowDrop(false); return }
    debounceRef.current = setTimeout(() => runSearch(q.trim()), 300)
  }

  function handleSearch(e: React.FormEvent) {
    e.preventDefault()
    const q = query.trim()
    if (!q) return
    setShowDrop(false)
    navigate(`/search?q=${encodeURIComponent(q)}`)
  }

  function goTo(path: string) {
    setShowDrop(false)
    setQuery('')
    setResults(null)
    navigate(path)
  }

  function handleKey(e: React.KeyboardEvent) {
    if (e.key === 'Escape') { setShowDrop(false); setQuery('') }
  }

  const hasResults = results && (results.posts.length + results.subreddits.length + results.users.length) > 0
  const initials = currentUser?.username.slice(0, 2).toUpperCase()

  return (
    <header className="bg-[#1a1a1b] sticky top-0 z-10 border-b border-[#343536]">
      <div className="max-w-6xl mx-auto px-4 h-12 flex items-center gap-4">

        <Link to="/" className="text-white font-bold text-lg tracking-tight shrink-0 hover:text-orange-400 transition-colors">
          geothread
        </Link>

        <div ref={searchRef} className="flex-1 max-w-xl mx-auto relative">
          <form onSubmit={handleSearch}>
            <div className="flex items-center bg-[#272729] border border-[#343536] hover:border-[#818384] focus-within:border-white rounded-full px-3 h-9 gap-2 transition-colors">
              <MagnifyingGlassIcon className="w-4 h-4 text-[#818384] shrink-0" />
              <input
                type="text"
                value={query}
                onChange={handleChange}
                onKeyDown={handleKey}
                onFocus={() => { if (hasResults) setShowDrop(true) }}
                placeholder="Search GeoThread"
                className="flex-1 bg-transparent text-sm text-white placeholder-[#818384] outline-none"
              />
              {searching && (
                <div className="w-3.5 h-3.5 border-2 border-[#818384] border-t-white rounded-full animate-spin shrink-0" />
              )}
            </div>
          </form>

          {showDrop && (
            <div className="absolute top-11 left-0 right-0 bg-[#1a1a1b] border border-[#343536] rounded-md shadow-2xl overflow-hidden z-30">
              {!hasResults ? (
                <p className="text-xs text-[#818384] px-4 py-3">No results for "{query}"</p>
              ) : (
                <>
                  {results!.posts.length > 0 && (
                    <section>
                      <p className="text-[10px] font-semibold text-[#818384] uppercase tracking-wider px-3 pt-2.5 pb-1">Posts</p>
                      {results!.posts.slice(0, 4).map(p => (
                        <button
                          key={p.post_id}
                          onClick={() => goTo(`/post/${p.post_id}`)}
                          className="w-full flex items-start gap-2.5 px-3 py-2 hover:bg-[#272729] transition-colors text-left"
                        >
                          <DocumentTextIcon className="w-4 h-4 text-[#818384] shrink-0 mt-0.5" />
                          <div className="min-w-0">
                            <p className="text-sm text-white truncate leading-tight">{p.title}</p>
                            <p className="text-[11px] text-[#818384] mt-0.5">r/{p.subreddit_name ?? p.subreddit_id}</p>
                          </div>
                        </button>
                      ))}
                    </section>
                  )}

                  {results!.subreddits.length > 0 && (
                    <section>
                      <p className="text-[10px] font-semibold text-[#818384] uppercase tracking-wider px-3 pt-2.5 pb-1">Communities</p>
                      {results!.subreddits.slice(0, 3).map(s => (
                        <button
                          key={s.subreddit_id}
                          onClick={() => goTo(`/r/${s.name}`)}
                          className="w-full flex items-center gap-2.5 px-3 py-2 hover:bg-[#272729] transition-colors text-left"
                        >
                          <UserGroupIcon className="w-4 h-4 text-[#818384] shrink-0" />
                          <div className="min-w-0">
                            <p className="text-sm text-white">r/{s.name}</p>
                            <p className="text-[11px] text-[#818384]">{s.subscriber_count.toLocaleString()} members</p>
                          </div>
                        </button>
                      ))}
                    </section>
                  )}

                  {results!.users.length > 0 && (
                    <section>
                      <p className="text-[10px] font-semibold text-[#818384] uppercase tracking-wider px-3 pt-2.5 pb-1">People</p>
                      {results!.users.slice(0, 3).map(u => (
                        <button
                          key={u.user_id}
                          onClick={() => goTo(`/u/${u.username}`)}
                          className="w-full flex items-center gap-2.5 px-3 py-2 hover:bg-[#272729] transition-colors text-left"
                        >
                          <UserCircleIcon className="w-5 h-5 text-[#818384] shrink-0" />
                          <p className="text-sm text-white">u/{u.username}</p>
                        </button>
                      ))}
                    </section>
                  )}

                  <button
                    onClick={() => { setShowDrop(false); navigate(`/search?q=${encodeURIComponent(query.trim())}`) }}
                    className="w-full text-left px-3 py-2.5 text-xs text-orange-400 hover:bg-[#272729] border-t border-[#343536] transition-colors"
                  >
                    See all results for "{query}"
                  </button>
                </>
              )}
            </div>
          )}
        </div>

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
