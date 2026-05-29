import type { Post, SortStrategy } from '../types'
import { haversine } from './geo'

const score = (p: Post) => p.upvotes - p.downvotes
const epoch = (iso: string) => new Date(iso).getTime() / 1000

function hotScore(p: Post): number {
  const s = score(p)
  const order = Math.log10(Math.max(Math.abs(s), 1))
  const sign = s > 0 ? 1 : s < 0 ? -1 : 0
  return sign * order + epoch(p.timestamp) / 45000
}

function risingScore(p: Post): number {
  const ageHours = (Date.now() / 1000 - epoch(p.timestamp)) / 3600
  if (ageHours > 24) return 0
  return score(p) / Math.pow(ageHours + 2, 1.5)
}

function controversialScore(p: Post): number {
  if (p.upvotes === 0 || p.downvotes === 0) return 0
  const magnitude = p.upvotes + p.downvotes
  const balance = Math.min(p.upvotes, p.downvotes) / Math.max(p.upvotes, p.downvotes)
  return magnitude * balance
}

export function sortPosts(
  posts: Post[],
  strategy: SortStrategy,
  userLat?: number,
  userLng?: number,
): Post[] {
  const scored = posts.map(p => {
    let priority: number
    switch (strategy) {
      case 'hot':           priority = hotScore(p); break
      case 'new':           priority = epoch(p.timestamp); break
      case 'top':           priority = score(p); break
      case 'rising':        priority = risingScore(p); break
      case 'controversial': priority = controversialScore(p); break
      case 'closest': {
        if (userLat == null || userLng == null || p.latitude == null || p.longitude == null) {
          priority = -Infinity
        } else {
          priority = -haversine(userLat, userLng, p.latitude, p.longitude)
        }
        break
      }
    }
    return { post: p, priority }
  })

  return scored.sort((a, b) => b.priority - a.priority).map(x => x.post)
}
