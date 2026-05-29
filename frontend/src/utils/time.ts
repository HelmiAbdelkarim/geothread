export function timeAgo(iso: string): string {
  const diff = Math.floor((Date.now() - new Date(iso).getTime()) / 1000)
  if (diff < 60) return `${diff}s ago`
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`
  return `${Math.floor(diff / 86400)}d ago`
}

export function memberSince(iso: string): string {
  const joined = new Date(iso)
  const months =
    (new Date().getFullYear() - joined.getFullYear()) * 12 +
    (new Date().getMonth() - joined.getMonth())
  if (months < 1) return 'joined this month'
  if (months < 12) return `member for ${months} month${months === 1 ? '' : 's'}`
  const years = Math.floor(months / 12)
  return `member for ${years} year${years === 1 ? '' : 's'}`
}
