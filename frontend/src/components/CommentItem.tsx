import { useState } from 'react'
import { Link } from 'react-router-dom'
import { ArrowUpIcon, ArrowDownIcon } from '@heroicons/react/24/outline'
import { ArrowUpIcon as ArrowUpSolid, ArrowDownIcon as ArrowDownSolid } from '@heroicons/react/24/solid'
import type { Comment } from '../types'
import { commentService } from '../services/commentService'
import { useAuth } from '../context/AuthContext'
import { timeAgo } from '../utils/time'

interface Props {
  comment: Comment
  depth?: number
  onReply?: (parentId: number, content: string) => Promise<void> | void
  onChanged?: () => Promise<void> | void
}

const BORDER_COLORS = [
  'border-l-[#ff4500]',
  'border-l-[#4fbdba]',
  'border-l-[#ffd635]',
  'border-l-[#7eb8f7]',
  'border-l-[#ff585b]',
  'border-l-[#46d160]',
]

export default function CommentItem({ comment, depth = 0, onReply, onChanged }: Props) {
  const { currentUser } = useAuth()
  const [pendingVote, setPendingVote] = useState(false)
  const [collapsed, setCollapsed] = useState(false)
  const [showReplies, setShowReplies] = useState(true)
  const [replyOpen, setReplyOpen] = useState(false)
  const [replyText, setReplyText] = useState('')
  const commentId = comment.comment_id ?? comment.id ?? 0
  const vote = (comment.user_vote ?? 0) as 1 | -1 | 0

  async function submitReply() {
    if (!replyText.trim() || !onReply) return
    await onReply(commentId, replyText.trim())
    setReplyText('')
    setReplyOpen(false)
  }

  async function handleVote(nextVote: 1 | -1) {
    if (!currentUser || pendingVote) return
    setPendingVote(true)
    try {
      await commentService.vote(
        currentUser.user_id,
        commentId,
        vote === nextVote ? 'remove' : nextVote === 1 ? 'up' : 'down',
      )
      await onChanged?.()
    } finally {
      setPendingVote(false)
    }
  }

  if (comment.is_deleted && comment.children.length === 0) return null

  const borderColor = BORDER_COLORS[depth % BORDER_COLORS.length]
  const hasReplies = comment.children.length > 0

  return (
    <div className={depth > 0 ? `pl-3 border-l-2 ${borderColor}` : ''}>
      <div className="py-1.5">
        <div className="flex items-center gap-2 text-xs text-[#818384] mb-1">
          <button
            onClick={() => setCollapsed(c => !c)}
            className="font-mono text-[#818384] hover:text-white leading-none w-4 text-center shrink-0"
            title={collapsed ? 'Expand' : 'Collapse'}
          >
            {collapsed ? '+' : '−'}
          </button>
          {comment.author_id ? (
            <Link to={`/u/${comment.author_username ?? comment.author_id}`} className="font-semibold text-white hover:underline">
              {comment.author_username ?? `user_${comment.author_id}`}
            </Link>
          ) : (
            <span className="font-semibold text-white">[deleted]</span>
          )}
          {comment.is_edited && <span className="italic text-[#818384]">edited</span>}
          <span className="text-[#818384]">•</span>
          <span>{timeAgo(comment.created_at)}</span>
        </div>

        {collapsed ? (
          <p className="text-xs text-[#818384] pl-6 italic">
            {hasReplies ? `${comment.children.length} repl${comment.children.length === 1 ? 'y' : 'ies'} hidden` : 'collapsed'}
          </p>
        ) : (
          <>
            <div className="pl-6">
              {comment.is_deleted ? (
                <p className="text-sm text-[#818384] italic">[deleted]</p>
              ) : (
                <p className="text-sm text-[#d7dadc] leading-relaxed">{comment.content}</p>
              )}

              <div className="flex items-center gap-3 mt-2">
                <div className="flex items-center gap-1">
                  <button
                    onClick={() => handleVote(1)}
                    disabled={pendingVote}
                    className={vote === 1 ? 'text-orange-500' : 'text-[#818384] hover:text-orange-500'}
                  >
                    {vote === 1 ? <ArrowUpSolid className="w-3.5 h-3.5" /> : <ArrowUpIcon className="w-3.5 h-3.5" />}
                  </button>
                  <span className={`text-xs font-bold ${vote === 1 ? 'text-orange-500' : vote === -1 ? 'text-blue-400' : 'text-[#818384]'}`}>
                    {comment.score ?? 0}
                  </span>
                  <button
                    onClick={() => handleVote(-1)}
                    disabled={pendingVote}
                    className={vote === -1 ? 'text-blue-400' : 'text-[#818384] hover:text-blue-400'}
                  >
                    {vote === -1 ? <ArrowDownSolid className="w-3.5 h-3.5" /> : <ArrowDownIcon className="w-3.5 h-3.5" />}
                  </button>
                </div>
                <button
                  onClick={() => setReplyOpen(o => !o)}
                  className="text-xs text-[#818384] hover:text-white font-medium"
                >
                  {replyOpen ? 'Cancel' : 'Reply'}
                </button>
                {hasReplies && (
                  <button
                    onClick={() => setShowReplies(s => !s)}
                    className="text-xs text-[#818384] hover:text-white font-medium"
                  >
                    {showReplies
                      ? `Hide ${comment.children.length} repl${comment.children.length === 1 ? 'y' : 'ies'}`
                      : `View ${comment.children.length} repl${comment.children.length === 1 ? 'y' : 'ies'}`}
                  </button>
                )}
              </div>
            </div>

            {replyOpen && (
              <div className="pl-6 mt-2 flex flex-col gap-2">
                <textarea
                  value={replyText}
                  onChange={e => setReplyText(e.target.value)}
                  onKeyDown={e => { if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) submitReply() }}
                  placeholder="Write a reply…"
                  rows={3}
                  className="w-full bg-[#272729] border border-[#343536] focus:border-[#818384] rounded text-sm text-[#d7dadc] placeholder-[#818384] p-2.5 outline-none resize-none transition-colors"
                />
                <div className="flex justify-end gap-2">
                  <button
                    onClick={() => { setReplyOpen(false); setReplyText('') }}
                    className="px-3 py-1 text-xs font-medium text-[#818384] hover:text-white transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={submitReply}
                    disabled={!replyText.trim()}
                    className="px-3 py-1 text-xs font-semibold rounded-full bg-orange-500 hover:bg-orange-600 text-white disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                  >
                    Reply
                  </button>
                </div>
              </div>
            )}

            {hasReplies && showReplies && (
              <div className="mt-2 flex flex-col gap-1">
                {comment.children.map(child => (
                  <CommentItem key={child.comment_id ?? child.id} comment={child} depth={depth + 1} onReply={onReply} onChanged={onChanged} />
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}
