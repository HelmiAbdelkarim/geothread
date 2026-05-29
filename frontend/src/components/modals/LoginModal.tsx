import { useState } from 'react'
import { XMarkIcon } from '@heroicons/react/24/outline'
import { useAuth } from '../../context/AuthContext'

interface Props {
  onClose: () => void
}

export default function LoginModal({ onClose }: Props) {
  const { loginByUsername } = useAuth()
  const [username, setUsername] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)
    try {
      await loginByUsername(username.trim())
      onClose()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Username not found.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60"
      onClick={onClose}
    >
      <div
        className="bg-[#1a1a1b] border border-[#343536] rounded-lg w-full max-w-sm mx-4 p-6 relative"
        onClick={e => e.stopPropagation()}
      >
        <button onClick={onClose} className="absolute top-4 right-4 text-[#818384] hover:text-white transition-colors">
          <XMarkIcon className="w-5 h-5" />
        </button>

        <h2 className="text-lg font-bold text-white mb-1">Log in</h2>
        <p className="text-xs text-[#818384] mb-6">By continuing, you agree to GeoThread's terms.</p>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-medium text-[#d7dadc]">Username</label>
            <input
              autoFocus
              value={username}
              onChange={e => { setUsername(e.target.value); setError('') }}
              placeholder="e.g. helmi_dev"
              className="bg-[#272729] border border-[#343536] focus:border-[#818384] rounded px-3 py-2 text-sm text-white placeholder-[#818384] outline-none transition-colors"
            />
            {error && <p className="text-xs text-red-400 leading-snug">{error}</p>}
          </div>
          <button
            type="submit"
            disabled={loading || !username.trim()}
            className="w-full py-2 rounded-full bg-orange-500 hover:bg-orange-600 text-white text-sm font-semibold transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Logging in...' : 'Log in'}
          </button>
        </form>

        <div className="mt-4 pt-4 border-t border-[#343536]">
          <p className="text-xs text-[#818384] text-center">
            Seeded users: helmi_dev · sara_algo · pedro_graphs · nour_isep · alex_cs · maya_fullstack
          </p>
        </div>
      </div>
    </div>
  )
}
