import { createContext, useContext, useEffect, useState } from 'react'
import type { Redditor } from '../types'
import { userService } from '../services/userService'

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
    let ignore = false
    userService.getAll()
      .then(users => {
        if (ignore) return
        setCurrentUser(users[0] ?? null)
        setError(null)
      })
      .catch(err => {
        if (!ignore) setError(err instanceof Error ? err.message : 'Failed to load users')
      })
      .finally(() => {
        if (!ignore) setLoading(false)
      })
    return () => { ignore = true }
  }, [])

  async function loginByUsername(username: string) {
    const user = await userService.getByUsername(username)
    setCurrentUser(user)
  }

  return (
    <AuthContext.Provider value={{
      currentUser,
      login: setCurrentUser,
      loginByUsername,
      loading,
      error,
      logout: () => setCurrentUser(null),
    }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
