import type { Redditor, Subreddit, Post, Comment } from '../types'

export const redditors: Redditor[] = [
  { user_id: 1, username: 'helmi_dev',     email: 'helmi@geo.io',  created_at: '2024-01-10T08:00:00Z', post_karma: 4200, comment_karma: 1800 },
  { user_id: 2, username: 'sara_algo',     email: 'sara@geo.io',   created_at: '2024-02-14T10:00:00Z', post_karma: 980,  comment_karma: 3200 },
  { user_id: 3, username: 'pedro_graphs',  email: 'pedro@geo.io',  created_at: '2024-03-01T09:00:00Z', post_karma: 150,  comment_karma: 620  },
  { user_id: 4, username: 'nour_isep',     email: 'nour@geo.io',   created_at: '2024-03-20T14:00:00Z', post_karma: 70,   comment_karma: 210  },
  { user_id: 5, username: 'alex_cs',       email: 'alex@geo.io',   created_at: '2024-04-01T11:00:00Z', post_karma: 2100, comment_karma: 950  },
  { user_id: 6, username: 'maya_fullstack',email: 'maya@geo.io',   created_at: '2024-04-10T09:00:00Z', post_karma: 340,  comment_karma: 1100 },
]

export const subreddits: Subreddit[] = [
  { subreddit_id: 1, name: 'r/algorithms', description: 'Graph theory, complexity, raw implementations.', created_at: '2024-01-01T00:00:00Z', subscriber_count: 142000 },
  { subreddit_id: 2, name: 'r/python',     description: 'Python news, tips and projects.',               created_at: '2024-01-01T00:00:00Z', subscriber_count: 980000 },
  { subreddit_id: 3, name: 'r/webdev',     description: 'Frontend, backend, devops.',                    created_at: '2024-01-01T00:00:00Z', subscriber_count: 430000 },
  { subreddit_id: 4, name: 'r/geothread',  description: 'GeoThread project discussion.',                 created_at: '2024-04-01T00:00:00Z', subscriber_count: 12     },
  { subreddit_id: 5, name: 'r/programming',description: 'General programming discussion.',               created_at: '2024-01-01T00:00:00Z', subscriber_count: 5400000},
]

const ago = (ms: number) => new Date(Date.now() - ms).toISOString()
const m = 60 * 1000
const h = 3600 * 1000
const d = 86400 * 1000

export const posts: Post[] = [
  {
    post_id: 1, author_id: 1, subreddit_id: 1,
    title: 'Why Dijkstra fails on negative weights — and what to use instead',
    content: 'A deep dive into why Dijkstra breaks with negative edges and how Bellman-Ford handles it. The key issue is the greedy relaxation assumption.',
    timestamp: ago(45 * m), upvotes: 3420, downvotes: 180, comments: 142,
    image_url: 'https://images.unsplash.com/photo-1516116216624-53e697fedbea?w=960&q=80',
    lat: 48.8584, lng: 2.2945, // Eiffel Tower ~0.7 km from centre
  },
  {
    post_id: 2, author_id: 2, subreddit_id: 2,
    title: 'I built a Reddit clone backend in pure Python — no graph libraries',
    content: 'For my algorithms class I implemented BFS, DFS, Dijkstra, and a priority-queue-based feed from scratch. Here is what I learned.',
    timestamp: ago(3 * h), upvotes: 1850, downvotes: 95, comments: 87,
    image_url: 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=960&q=80',
    lat: 48.8867, lng: 2.3431, // Montmartre ~3.4 km
  },
  {
    post_id: 3, author_id: 3, subreddit_id: 3,
    title: 'Tailwind v4 is actually great — here is what changed',
    content: 'Just migrated a large project. The new @import approach and Vite plugin are clean. CSS-first config is a big improvement.',
    timestamp: ago(12 * h), upvotes: 920, downvotes: 310, comments: 64,
    image_url: 'https://images.unsplash.com/photo-1461749280684-dccba630e2f6?w=960&q=80',
    lat: 48.8534, lng: 2.3332, // Saint-Germain ~0.4 km
  },
  {
    post_id: 4, author_id: 1, subreddit_id: 4,
    title: 'GeoThread ASNAP engine — first working demo',
    content: 'Feed sorting with hot/new/top/rising/controversial is live. Comment tree traversal next. All algorithms are raw Python, no libraries.',
    timestamp: ago(10 * m), upvotes: 8, downvotes: 1, comments: 3,
    lat: 48.8574, lng: 2.3578, // Le Marais ~0.1 km
  },
  {
    post_id: 5, author_id: 4, subreddit_id: 1,
    title: 'Union-Find vs label propagation for community detection — which is better?',
    content: 'Both work. Union-Find is simpler and O(α(n)) amortized. Label propagation gives richer clusters but is harder to tune.',
    timestamp: ago(36 * h), upvotes: 610, downvotes: 580, comments: 201,
    lat: 48.8924, lng: 2.2381, // La Défense ~9.4 km
  },
  {
    post_id: 6, author_id: 5, subreddit_id: 5,
    title: 'Recursion vs iteration — when does it actually matter?',
    content: 'Stack overflow is the obvious risk, but the real question is readability vs control. Here is my take after 10 years.',
    timestamp: ago(2 * h), upvotes: 2100, downvotes: 140, comments: 310,
    image_url: 'https://images.unsplash.com/photo-1504639725590-34d0984388bd?w=960&q=80',
    lat: 48.8049, lng: 2.1204, // Versailles ~18 km
  },
  {
    post_id: 7, author_id: 6, subreddit_id: 3,
    title: 'React Server Components finally make sense to me — here is the mental model',
    content: 'After months of confusion I finally get it. The key is thinking about the component tree as two separate trees that get merged.',
    timestamp: ago(5 * h), upvotes: 1430, downvotes: 210, comments: 95,
    image_url: 'https://images.unsplash.com/photo-1633356122544-f134324a6cee?w=960&q=80',
    lat: 48.8396, lng: 2.2456, // Boulogne ~11 km
  },
  {
    post_id: 8, author_id: 2, subreddit_id: 2,
    title: 'Python 3.14 is faster than ever — here are the benchmarks',
    content: 'The new tail-call interpreter brings 15–40% speedups on real workloads. GIL removal is also stabilizing.',
    timestamp: ago(8 * h), upvotes: 4800, downvotes: 90, comments: 412,
    image_url: 'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=960&q=80',
    // no location — global post
  },
  {
    post_id: 9, author_id: 3, subreddit_id: 1,
    title: 'Implementing a min-heap from scratch in 30 lines of Python',
    content: 'No heapq module, just raw list manipulation. Great for understanding the underlying structure before using stdlib.',
    timestamp: ago(20 * h), upvotes: 780, downvotes: 45, comments: 56,
    // no location — global post
  },
  {
    post_id: 10, author_id: 5, subreddit_id: 5,
    title: 'The two-sum problem has a O(n) solution — most people miss it',
    content: 'Everyone thinks hash map, which is correct. But there is a one-pass variant that is even cleaner. Here is the walkthrough.',
    timestamp: ago(1 * d), upvotes: 3200, downvotes: 120, comments: 278,
    image_url: 'https://images.unsplash.com/photo-1509228468518-180dd4864904?w=960&q=80',
    // no location — global post
  },
]

export const comments: Comment[] = [
  // Post 1 — deep tree to showcase tree traversal
  {
    id: 1, content: 'Great explanation. The key insight is that Dijkstra uses a greedy relaxation that assumes all weights are non-negative.',
    author_id: 2, post_id: 1, parent_comment_id: null,
    created_at: ago(40 * m), updated_at: ago(40 * m), is_edited: false, is_deleted: false,
    children: [
      {
        id: 5, content: 'Exactly. And Bellman-Ford runs in O(VE) instead of O((V+E) log V), which matters at scale.',
        author_id: 3, post_id: 1, parent_comment_id: 1,
        created_at: ago(35 * m), updated_at: ago(35 * m), is_edited: false, is_deleted: false,
        children: [
          {
            id: 8, content: 'Worth noting: Bellman-Ford also detects negative cycles, which Dijkstra cannot do at all.',
            author_id: 5, post_id: 1, parent_comment_id: 5,
            created_at: ago(30 * m), updated_at: ago(30 * m), is_edited: false, is_deleted: false,
            children: [
              {
                id: 11, content: 'This is the real reason to use it. If your graph might have negative cycles you have no choice.',
                author_id: 1, post_id: 1, parent_comment_id: 8,
                created_at: ago(25 * m), updated_at: ago(25 * m), is_edited: false, is_deleted: false,
                children: [
                  {
                    id: 14, content: 'Unless you use Johnson\'s algorithm, which handles negative weights by reweighting the graph first.',
                    author_id: 6, post_id: 1, parent_comment_id: 11,
                    created_at: ago(20 * m), updated_at: ago(20 * m), is_edited: false, is_deleted: false,
                    children: [
                      {
                        id: 16, content: 'Johnson\'s is O(V² log V + VE), which is better than running Bellman-Ford V times for dense graphs.',
                        author_id: 2, post_id: 1, parent_comment_id: 14,
                        created_at: ago(15 * m), updated_at: ago(15 * m), is_edited: false, is_deleted: false,
                        children: [],
                      },
                    ],
                  },
                ],
              },
            ],
          },
          {
            id: 12, content: 'For SSSP on DAGs you can also use topological sort + relaxation in O(V+E).',
            author_id: 4, post_id: 1, parent_comment_id: 5,
            created_at: ago(28 * m), updated_at: ago(28 * m), is_edited: false, is_deleted: false,
            children: [
              {
                id: 15, content: 'Nice point. Topological order guarantees you never relax an edge before its source is finalized.',
                author_id: 3, post_id: 1, parent_comment_id: 12,
                created_at: ago(22 * m), updated_at: ago(22 * m), is_edited: false, is_deleted: false,
                children: [],
              },
            ],
          },
        ],
      },
      {
        id: 9, content: 'Good point. The practical tradeoff is Dijkstra with a Fibonacci heap vs Bellman-Ford on sparse graphs.',
        author_id: 6, post_id: 1, parent_comment_id: 1,
        created_at: ago(33 * m), updated_at: ago(33 * m), is_edited: false, is_deleted: false,
        children: [],
      },
    ],
  },
  {
    id: 2, content: 'What about A*? Is it also broken on negative weights?',
    author_id: 4, post_id: 1, parent_comment_id: null,
    created_at: ago(30 * m), updated_at: ago(30 * m), is_edited: false, is_deleted: false,
    children: [
      {
        id: 6, content: 'Yes, A* has the same problem. It is essentially Dijkstra with a heuristic added to the priority.',
        author_id: 1, post_id: 1, parent_comment_id: 2,
        created_at: ago(25 * m), updated_at: ago(25 * m), is_edited: false, is_deleted: false,
        children: [
          {
            id: 10, content: 'The heuristic must be admissible (never overestimates) AND consistent for A* to be optimal.',
            author_id: 2, post_id: 1, parent_comment_id: 6,
            created_at: ago(18 * m), updated_at: ago(18 * m), is_edited: false, is_deleted: false,
            children: [
              {
                id: 13, content: 'Consistency is a stronger condition than admissibility. It implies admissibility but not vice versa.',
                author_id: 5, post_id: 1, parent_comment_id: 10,
                created_at: ago(12 * m), updated_at: ago(12 * m), is_edited: false, is_deleted: false,
                children: [],
              },
            ],
          },
        ],
      },
    ],
  },
  {
    id: 3, content: 'Great post. I would also mention SPFA (Bellman-Ford with a queue) which is faster in practice on sparse graphs.',
    author_id: 5, post_id: 1, parent_comment_id: null,
    created_at: ago(20 * m), updated_at: ago(20 * m), is_edited: false, is_deleted: false,
    children: [
      {
        id: 7, content: 'SPFA worst case is still O(VE) and it can degrade badly on adversarial inputs.',
        author_id: 3, post_id: 1, parent_comment_id: 3,
        created_at: ago(15 * m), updated_at: ago(15 * m), is_edited: false, is_deleted: false,
        children: [],
      },
    ],
  },
  {
    id: 4, content: 'Bookmarked. This is exactly the kind of comparison that is missing from most textbooks.',
    author_id: 6, post_id: 1, parent_comment_id: null,
    created_at: ago(10 * m), updated_at: ago(10 * m), is_edited: false, is_deleted: false,
    children: [],
  },
]

export const userById = (id: number) => redditors.find(u => u.user_id === id)
export const subredditById = (id: number) => subreddits.find(s => s.subreddit_id === id)
export const postById = (id: number) => posts.find(p => p.post_id === id)
export const commentsByPost = (postId: number) => comments.filter(c => c.post_id === postId)
