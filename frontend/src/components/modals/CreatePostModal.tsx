import { useState, useEffect, useRef } from 'react'
import { XMarkIcon, PhotoIcon } from '@heroicons/react/24/outline'
import { useData } from '../../context/DataContext'
import { useAuth } from '../../context/AuthContext'

interface Props {
  onClose: () => void
}

export default function CreatePostModal({ onClose }: Props) {
  const { subreddits, addPost } = useData()
  const { currentUser } = useAuth()
  const [title, setTitle] = useState('')
  const [body, setBody] = useState('')
  const [imageUrl, setImageUrl] = useState('')
  const [subredditId, setSubredditId] = useState(subreddits[0]?.subreddit_id ?? 1)
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const backdropRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose() }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [onClose])

  async function handleSubmit() {
    if (!title.trim()) return
    if (!currentUser) {
      setError('Log in before creating a post.')
      return
    }
    setSubmitting(true)
    try {
      const imageLine = imageUrl.trim() ? `\n\nImage: ${imageUrl.trim()}` : ''
      await addPost(subredditId, title.trim(), `${body.trim()}${imageLine}`.trim())
      onClose()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create post.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div
      ref={backdropRef}
      onClick={e => { if (e.target === backdropRef.current) onClose() }}
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 px-4"
    >
      <div className="bg-[#1a1a1b] border border-[#343536] rounded-lg w-full max-w-xl shadow-2xl">
        <div className="flex items-center justify-between px-4 py-3 border-b border-[#343536]">
          <h2 className="text-sm font-semibold text-white">Create a Post</h2>
          <button onClick={onClose} className="text-[#818384] hover:text-white transition-colors">
            <XMarkIcon className="w-5 h-5" />
          </button>
        </div>

        <div className="p-4 flex flex-col gap-3">
          <select
            value={subredditId}
            onChange={e => setSubredditId(Number(e.target.value))}
            className="bg-[#272729] border border-[#343536] focus:border-[#818384] text-white text-sm rounded px-3 py-2 outline-none transition-colors"
          >
            {subreddits.map(s => (
              <option key={s.subreddit_id} value={s.subreddit_id}>{s.name}</option>
            ))}
          </select>

          <div>
            <input
              type="text"
              value={title}
              onChange={e => setTitle(e.target.value)}
              placeholder="Title *"
              maxLength={300}
              className="w-full bg-[#272729] border border-[#343536] focus:border-[#818384] text-white text-sm rounded px-3 py-2 outline-none placeholder-[#818384] transition-colors"
            />
            <p className="text-[10px] text-[#818384] text-right mt-1">{title.length}/300</p>
          </div>

          <textarea
            value={body}
            onChange={e => setBody(e.target.value)}
            placeholder="Text (optional)"
            rows={5}
            className="w-full bg-[#272729] border border-[#343536] focus:border-[#818384] text-white text-sm rounded px-3 py-2 outline-none placeholder-[#818384] resize-none transition-colors"
          />

          <div className="flex items-center gap-2">
            <PhotoIcon className="w-4 h-4 text-[#818384] shrink-0" />
            <input
              type="text"
              value={imageUrl}
              onChange={e => setImageUrl(e.target.value)}
              placeholder="Image URL (optional)"
              className="flex-1 bg-[#272729] border border-[#343536] focus:border-[#818384] text-white text-sm rounded px-3 py-2 outline-none placeholder-[#818384] transition-colors"
            />
          </div>

          {error && <p className="text-xs text-red-400">{error}</p>}

          <div className="flex justify-end gap-2 pt-1">
            <button onClick={onClose} className="px-4 py-1.5 text-sm font-medium text-[#818384] hover:text-white transition-colors">
              Cancel
            </button>
            <button
              onClick={handleSubmit}
              disabled={!title.trim() || submitting}
              className="px-5 py-1.5 text-sm font-semibold rounded-full bg-orange-500 hover:bg-orange-600 text-white disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              {submitting ? 'Posting...' : 'Post'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
