import { createContext, useContext, useEffect, useState } from 'react'
import type { Redditor } from '../types'
import { userService } from '../services/userService'

const STORAGE_KEY = 'geothread_user_id'

interface AuthContextType {
  currentUser: Redditor | null
  login: (user: Redditor) => void
  loginByUsername: (username: string) => Promise<void>
  loading: boolean
  error: string | null
  logout: () => void
}

const AuthContext = createContext<AuthContextType | null>(null)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [currentUser, setCurrentUser] = useState<Redditor | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const savedId = localStorage.getItem(STORAGE_KEY)
    if (!savedId) {
      setLoading(false)
      return
    }
    userService.getAll()
      .then(users => {
        const found = users.find(u => String(u.user_id) === savedId)
        setCurrentUser(found ?? null)
        if (!found) localStorage.removeItem(STORAGE_KEY)
      })
      .catch(() => localStorage.removeItem(STORAGE_KEY))
      .finally(() => setLoading(false))
  }, [])

  function login(user: Redditor) {
    setCurrentUser(user)
    localStorage.setItem(STORAGE_KEY, String(user.user_id))
  }

  async function loginByUsername(username: string) {
    const user = await userService.getByUsername(username)
    login(user)
  }

  function logout() {
    setCurrentUser(null)
    localStorage.removeItem(STORAGE_KEY)
    setError(null)
  }

  return (
    <AuthContext.Provider value={{ currentUser, login, loginByUsername, loading, error, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
