import type { CVProfile, MatchedJob } from './types'

export interface HistoryEntry {
  ts: number
  profile: CVProfile
  jobs: MatchedJob[]
  sourcesUsed: string[]
  sourcesFailed: string[]
  usedLlm: boolean
}

const KEY = 'cv2job.history'
const MAX_ENTRIES = 10
const DESCRIPTION_CHARS = 200

export function loadHistory(): HistoryEntry[] {
  try {
    const raw = localStorage.getItem(KEY)
    const parsed = raw ? JSON.parse(raw) : []
    return Array.isArray(parsed) ? parsed : []
  } catch {
    return []
  }
}

export function saveRun(entry: HistoryEntry): HistoryEntry[] {
  const trimmed: HistoryEntry = {
    ...entry,
    jobs: entry.jobs.map((job) => ({
      ...job,
      description: job.description.slice(0, DESCRIPTION_CHARS),
    })),
  }
  const history = [trimmed, ...loadHistory()].slice(0, MAX_ENTRIES)
  try {
    localStorage.setItem(KEY, JSON.stringify(history))
  } catch {
    // quota exceeded — drop oldest entries and retry once
    try {
      localStorage.setItem(KEY, JSON.stringify(history.slice(0, 3)))
    } catch {
      // give up silently; history is a convenience feature
    }
  }
  return history
}

export function clearHistory(): void {
  try {
    localStorage.removeItem(KEY)
  } catch {
    // ignore
  }
}
