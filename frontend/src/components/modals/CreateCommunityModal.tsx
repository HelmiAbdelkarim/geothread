import { useState, useEffect, useRef } from 'react'
import { XMarkIcon } from '@heroicons/react/24/outline'
import { useData } from '../../context/DataContext'

interface Props {
  onClose: () => void
}

const TOPICS = ['Technology', 'Science', 'Gaming', 'Art', 'Music', 'Sports', 'Education', 'Local', 'Other']

export default function CreateCommunityModal({ onClose }: Props) {
  const { addSubreddit } = useData()
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [topic, setTopic] = useState(TOPICS[0])
  const [nameError, setNameError] = useState('')
  const [submitError, setSubmitError] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const backdropRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose() }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [onClose])

  function validateName(raw: string): string {
    const cleaned = raw.replace(/\s/g, '_').toLowerCase()
    if (cleaned.length < 3) return 'Name must be at least 3 characters'
    if (!/^[a-z0-9_]+$/.test(cleaned)) return 'Only letters, numbers and underscores'
    return ''
  }

  function handleNameChange(raw: string) {
    setName(raw)
    setNameError(raw.length > 0 ? validateName(raw) : '')
  }

  async function handleSubmit() {
    const error = validateName(name)
    if (error) { setNameError(error); return }
    setSubmitting(true)
    try {
      await addSubreddit(name.replace(/\s/g, '_').toLowerCase(), description.trim() || topic)
      onClose()
    } catch (err) {
      setSubmitError(err instanceof Error ? err.message : 'Failed to create community.')
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
      <div className="bg-[#1a1a1b] border border-[#343536] rounded-lg w-full max-w-md shadow-2xl">
        <div className="flex items-center justify-between px-4 py-3 border-b border-[#343536]">
          <h2 className="text-sm font-semibold text-white">Create a Community</h2>
          <button onClick={onClose} className="text-[#818384] hover:text-white transition-colors">
            <XMarkIcon className="w-5 h-5" />
          </button>
        </div>

        <div className="p-4 flex flex-col gap-4">
          <div>
            <label className="block text-xs font-medium text-[#d7dadc] mb-1.5">
              Community name <span className="text-red-400">*</span>
            </label>
            <div className="flex items-center bg-[#272729] border border-[#343536] focus-within:border-[#818384] rounded px-3 py-2 gap-1 transition-colors">
              <span className="text-[#818384] text-sm">r/</span>
              <input
                type="text"
                value={name}
                onChange={e => handleNameChange(e.target.value)}
                placeholder="community_name"
                maxLength={21}
                className="flex-1 bg-transparent text-white text-sm outline-none placeholder-[#818384]"
              />
              <span className="text-[10px] text-[#818384] shrink-0">{name.length}/21</span>
            </div>
            {nameError && <p className="text-xs text-red-400 mt-1">{nameError}</p>}
            <p className="text-[10px] text-[#818384] mt-1">Community names cannot be changed after creation.</p>
          </div>

          <div>
            <label className="block text-xs font-medium text-[#d7dadc] mb-1.5">Description</label>
            <textarea
              value={description}
              onChange={e => setDescription(e.target.value)}
              placeholder="What is your community about?"
              rows={3}
              className="w-full bg-[#272729] border border-[#343536] focus:border-[#818384] text-white text-sm rounded px-3 py-2 outline-none placeholder-[#818384] resize-none transition-colors"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-[#d7dadc] mb-1.5">Topic</label>
            <select
              value={topic}
              onChange={e => setTopic(e.target.value)}
              className="w-full bg-[#272729] border border-[#343536] focus:border-[#818384] text-white text-sm rounded px-3 py-2 outline-none transition-colors"
            >
              {TOPICS.map(t => <option key={t}>{t}</option>)}
            </select>
          </div>

          {submitError && <p className="text-xs text-red-400">{submitError}</p>}

          <div className="flex justify-end gap-2 pt-1">
            <button onClick={onClose} className="px-4 py-1.5 text-sm font-medium text-[#818384] hover:text-white transition-colors">
              Cancel
            </button>
            <button
              onClick={handleSubmit}
              disabled={!name.trim() || !!nameError || submitting}
              className="px-5 py-1.5 text-sm font-semibold rounded-full bg-orange-500 hover:bg-orange-600 text-white disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              {submitting ? 'Creating...' : 'Create Community'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
