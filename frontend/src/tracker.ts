import type { MatchedJob } from './types'

export type TrackStatus = 'saved' | 'applied' | 'interview' | 'offer' | 'rejected'

export const STATUS_LABELS: Record<TrackStatus, string> = {
  saved: 'Saved',
  applied: 'Applied',
  interview: 'Interview',
  offer: 'Offer',
  rejected: 'Rejected',
}

export interface TrackedJob {
  job: MatchedJob
  status: TrackStatus
  note: string
  addedAt: number
  appliedAt: number | null
  updatedAt: number
}

const KEY = 'cv2job.tracker'
const MAX_ENTRIES = 200
const DESCRIPTION_CHARS = 200

export function loadTracker(): TrackedJob[] {
  try {
    const raw = localStorage.getItem(KEY)
    const parsed = raw ? JSON.parse(raw) : []
    return Array.isArray(parsed) ? parsed : []
  } catch {
    return []
  }
}

function persist(entries: TrackedJob[]): TrackedJob[] {
  const trimmed = entries.slice(0, MAX_ENTRIES)
  try {
    localStorage.setItem(KEY, JSON.stringify(trimmed))
  } catch {
    try {
      localStorage.setItem(KEY, JSON.stringify(trimmed.slice(0, 50)))
    } catch {
      // storage unavailable — tracker becomes session-only
    }
  }
  return trimmed
}

/** Add a job with the given status, or update the status if already tracked. */
export function trackJob(job: MatchedJob, status: TrackStatus): TrackedJob[] {
  const now = Date.now()
  const entries = loadTracker()
  const existing = entries.find((e) => e.job.id === job.id)
  if (existing) {
    existing.status = status
    existing.updatedAt = now
    if (status === 'applied' && existing.appliedAt === null) {
      existing.appliedAt = now
    }
    return persist(entries)
  }
  const entry: TrackedJob = {
    job: { ...job, description: job.description.slice(0, DESCRIPTION_CHARS) },
    status,
    note: '',
    addedAt: now,
    appliedAt: status === 'applied' ? now : null,
    updatedAt: now,
  }
  return persist([entry, ...entries])
}

export function updateTracked(
  jobId: string,
  patch: Partial<Pick<TrackedJob, 'status' | 'note'>>,
): TrackedJob[] {
  const now = Date.now()
  const entries = loadTracker()
  const entry = entries.find((e) => e.job.id === jobId)
  if (entry) {
    if (patch.status !== undefined) {
      entry.status = patch.status
      if (patch.status === 'applied' && entry.appliedAt === null) {
        entry.appliedAt = now
      }
    }
    if (patch.note !== undefined) entry.note = patch.note
    entry.updatedAt = now
  }
  return persist(entries)
}

export function removeTracked(jobId: string): TrackedJob[] {
  return persist(loadTracker().filter((e) => e.job.id !== jobId))
}
