import type {
  MatchRequest,
  MatchResponse,
  ParseResponse,
  ProvidersResponse,
} from '../types'

export class ApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let resp: Response
  try {
    resp = await fetch(path, init)
  } catch {
    throw new ApiError(
      0,
      'Could not reach the server — is the backend running on port 8000?',
    )
  }
  if (!resp.ok) {
    let detail = `Request failed (${resp.status})`
    try {
      const body = await resp.json()
      if (typeof body.detail === 'string') detail = body.detail
    } catch {
      // non-JSON error body; keep generic message
    }
    throw new ApiError(resp.status, detail)
  }
  return resp.json() as Promise<T>
}

export function getProviders(): Promise<ProvidersResponse> {
  return request('/api/providers')
}

export function parseCv(file: File): Promise<ParseResponse> {
  const form = new FormData()
  form.append('file', file)
  return request('/api/cv/parse', { method: 'POST', body: form })
}

export function matchJobs(req: MatchRequest): Promise<MatchResponse> {
  return request('/api/jobs/match', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  })
}
