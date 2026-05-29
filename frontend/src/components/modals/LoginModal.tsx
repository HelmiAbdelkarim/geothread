import { useEffect, useState } from 'react'
import { XMarkIcon, MapPinIcon } from '@heroicons/react/24/outline'
import { useAuth } from '../../context/AuthContext'
import { userService } from '../../services/userService'
import type { Redditor } from '../../types'

const GRADIENTS = [
  'from-orange-400 to-red-500',
  'from-blue-400 to-purple-500',
  'from-green-400 to-teal-500',
  'from-pink-400 to-rose-500',
  'from-yellow-400 to-orange-500',
  'from-indigo-400 to-blue-500',
]

const LOCATIONS: Record<string, string> = {
  helmi_dev:      'Issy-les-Moulineaux',
  sara_algo:      '15ème arrondissement',
  pedro_graphs:   'Ivry-sur-Seine',
  nour_isep:      'La Défense',
  alex_cs:        'New York',
  maya_fullstack: 'Seattle',
}

interface Props {
  onClose: () => void
}

export default function LoginModal({ onClose }: Props) {
  const { login } = useAuth()
  const [users, setUsers] = useState<Redditor[]>([])
  const [loadingUsers, setLoadingUsers] = useState(true)
  const [loggingIn, setLoggingIn] = useState<number | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    userService.getAll()
      .then(setUsers)
      .catch(() => setError('Failed to load users.'))
      .finally(() => setLoadingUsers(false))
  }, [])

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose() }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [onClose])

  async function handlePick(user: Redditor) {
    setLoggingIn(user.user_id)
    try {
      login(user)
      onClose()
    } catch {
      setError('Login failed.')
    } finally {
      setLoggingIn(null)
    }
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 px-4"
      onClick={onClose}
    >
      <div
        className="bg-[#1a1a1b] border border-[#343536] rounded-lg w-full max-w-sm shadow-2xl"
        onClick={e => e.stopPropagation()}
      >
        <div className="flex items-center justify-between px-5 py-4 border-b border-[#343536]">
          <h2 className="text-sm font-semibold text-white">Choose your account</h2>
          <button onClick={onClose} className="text-[#818384] hover:text-white transition-colors">
            <XMarkIcon className="w-5 h-5" />
          </button>
        </div>

        <div className="p-3 flex flex-col gap-1.5">
          {error && <p className="text-xs text-red-400 px-2 pb-1">{error}</p>}

          {loadingUsers ? (
            <p className="text-xs text-[#818384] text-center py-6">Loading accounts…</p>
          ) : (
            users.map((user, i) => {
              const gradient = GRADIENTS[i % GRADIENTS.length]
              const city = LOCATIONS[user.username]
              const isLoading = loggingIn === user.user_id

              return (
                <button
                  key={user.user_id}
                  onClick={() => handlePick(user)}
                  disabled={loggingIn !== null}
                  className="flex items-center gap-3 px-3 py-2.5 rounded-md hover:bg-[#272729] transition-colors text-left disabled:opacity-50 group"
                >
                  <div className={`w-9 h-9 rounded-full bg-gradient-to-br ${gradient} flex items-center justify-center shrink-0 text-white text-sm font-bold`}>
                    {user.username[0].toUpperCase()}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold text-white">u/{user.username}</p>
                    {city && (
                      <p className="text-[11px] text-[#818384] flex items-center gap-0.5 mt-0.5">
                        <MapPinIcon className="w-3 h-3 shrink-0" />
                        {city}
                      </p>
                    )}
                  </div>
                  <span className="text-[11px] text-[#818384] shrink-0 group-hover:text-[#d7dadc] transition-colors">
                    {isLoading ? 'Signing in…' : `${(user.post_karma + user.comment_karma).toLocaleString()} karma`}
                  </span>
                </button>
              )
            })
          )}
        </div>
      </div>
    </div>
  )
}
