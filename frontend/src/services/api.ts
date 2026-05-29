const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api'

interface RequestOptions extends Omit<RequestInit, 'body'> {
  body?: unknown
  userId?: number | null
  query?: Record<string, string | number | boolean | null | undefined>
}

export class ApiError extends Error {
  status: number

  constructor(message: string, status: number) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

export async function apiRequest<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { userId, query, headers, body, ...init } = options
  const url = new URL(`${API_BASE_URL}${path}`)

  if (query) {
    for (const [key, value] of Object.entries(query)) {
      if (value !== null && value !== undefined) url.searchParams.set(key, String(value))
    }
  }

  const requestHeaders = new Headers(headers)
  if (userId) requestHeaders.set('X-User-Id', String(userId))
  if (body && !requestHeaders.has('Content-Type')) requestHeaders.set('Content-Type', 'application/json')

  const response = await fetch(url, {
    ...init,
    headers: requestHeaders,
    body: (body && typeof body !== 'string' ? JSON.stringify(body) : body) as BodyInit | undefined,
  })

  if (!response.ok) {
    let message = `Request failed with status ${response.status}`
    try {
      const data = await response.json()
      message = typeof data.detail === 'string' ? data.detail : message
    } catch {
      // Keep the generic message when the backend returns no JSON body.
    }
    throw new ApiError(message, response.status)
  }

  if (response.status === 204) return undefined as T
  return response.json() as Promise<T>
}
