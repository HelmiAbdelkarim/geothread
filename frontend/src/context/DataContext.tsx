import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import type { BackendSortStrategy, Post, Redditor, Subreddit, SubredditRecommendation, UserStats } from '../types'
import { postService } from '../services/postService'
import { subredditService } from '../services/subredditService'
import { userService } from '../services/userService'
import { useAuth } from './AuthContext'

interface DataContextType {
  posts: Post[]
  subreddits: Subreddit[]
  users: Redditor[]
  recommendations: SubredditRecommendation[]
  stats: UserStats | null
  loading: boolean
  error: string | null
  sort: BackendSortStrategy
  userById: Map<number, Redditor>
  subredditById: Map<number, Subreddit>
  subscribedIds: Set<number>
  setSort: (sort: BackendSortStrategy) => void
  refreshAll: () => Promise<void>
  refreshFeed: () => Promise<void>
  addPost: (subredditId: number, title: string, content: string, latitude?: number, longitude?: number, locationName?: string) => Promise<Post>
  addSubreddit: (name: string, description: string) => Promise<Subreddit>
  votePost: (postId: number, direction: 'up' | 'down' | 'remove') => Promise<void>
  subscribe: (subredditId: number) => Promise<void>
  unsubscribe: (subredditId: number) => Promise<void>
}

const DataContext = createContext<DataContextType | null>(null)

export function DataProvider({ children }: { children: React.ReactNode }) {
  const { currentUser } = useAuth()
  const [posts, setPosts] = useState<Post[]>([])
  const [subreddits, setSubreddits] = useState<Subreddit[]>([])
  const [users, setUsers] = useState<Redditor[]>([])
  const [recommendations, setRecommendations] = useState<SubredditRecommendation[]>([])
  const [stats, setStats] = useState<UserStats | null>(null)
  const [subscribedIds, setSubscribedIds] = useState<Set<number>>(new Set())
  const [sort, setSort] = useState<BackendSortStrategy>('hot')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const userById = useMemo(() => new Map(users.map(user => [user.user_id, user])), [users])
  const subredditById = useMemo(() => new Map(subreddits.map(sub => [sub.subreddit_id, sub])), [subreddits])

  const refreshFeed = useCallback(async () => {
    const nextPosts = await postService.getFeed(currentUser?.user_id, sort, 100)
    setPosts(nextPosts)
  }, [currentUser, sort])

  const refreshAll = useCallback(async () => {
    setLoading(true)
    try {
      const [nextUsers, nextSubreddits, nextPosts] = await Promise.all([
        userService.getAll(),
        subredditService.getAll(),
        postService.getFeed(currentUser?.user_id, sort, 100),
      ])
      setUsers(nextUsers)
      setSubreddits(nextSubreddits)
      setPosts(nextPosts)

      if (currentUser) {
        const [nextRecommendations, nextStats, nextSubIds] = await Promise.all([
          subredditService.recommendations(currentUser.user_id),
          userService.getStats(currentUser.user_id),
          userService.getSubscribedIds(currentUser.user_id),
        ])
        setRecommendations(nextRecommendations)
        setStats(nextStats)
        setSubscribedIds(new Set(nextSubIds))
      } else {
        setRecommendations([])
        setStats(null)
        setSubscribedIds(new Set())
      }

      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load backend data')
    } finally {
      setLoading(false)
    }
  }, [currentUser, sort])

  useEffect(() => {
    refreshAll()
  }, [refreshAll])

  async function addPost(subredditId: number, title: string, content: string, latitude?: number, longitude?: number, locationName?: string) {
    if (!currentUser) throw new Error('Log in before creating a post.')
    const post = await postService.create(currentUser.user_id, subredditId, title, content, latitude, longitude, locationName)
    await refreshAll()
    return post
  }

  async function addSubreddit(name: string, description: string) {
    if (!currentUser) throw new Error('Log in before creating a community.')
    const sub = await subredditService.create(currentUser.user_id, name, description)
    await refreshAll()
    return sub
  }

  async function votePost(postId: number, direction: 'up' | 'down' | 'remove') {
    if (!currentUser) throw new Error('Log in before voting.')
    await postService.vote(currentUser.user_id, postId, direction)
    await refreshFeed()
  }

  async function subscribe(subredditId: number) {
    if (!currentUser) throw new Error('Log in before joining a community.')
    await subredditService.subscribe(currentUser.user_id, subredditId)
    setSubscribedIds(prev => new Set([...prev, subredditId]))
    await refreshAll()
  }

  async function unsubscribe(subredditId: number) {
    if (!currentUser) throw new Error('Log in before leaving a community.')
    await subredditService.unsubscribe(currentUser.user_id, subredditId)
    setSubscribedIds(prev => { const next = new Set(prev); next.delete(subredditId); return next })
    await refreshAll()
  }

  return (
    <DataContext.Provider value={{
      posts,
      subreddits,
      users,
      recommendations,
      stats,
      loading,
      error,
      sort,
      userById,
      subredditById,
      subscribedIds,
      setSort,
      refreshAll,
      refreshFeed,
      addPost,
      addSubreddit,
      votePost,
      subscribe,
      unsubscribe,
    }}>
      {children}
    </DataContext.Provider>
  )
}

export function useData() {
  const ctx = useContext(DataContext)
  if (!ctx) throw new Error('useData must be used within DataProvider')
  return ctx
}
