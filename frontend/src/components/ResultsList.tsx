import { useState } from 'react'
import type { MatchedJob } from '../types'
import JobCard from './JobCard'

interface Props {
  jobs: MatchedJob[]
  sourcesUsed: string[]
  sourcesFailed: string[]
  usedLlm: boolean
  onBackToProfile: () => void
  onStartOver: () => void
}

export default function ResultsList({
  jobs,
  sourcesUsed,
  sourcesFailed,
  usedLlm,
  onBackToProfile,
  onStartOver,
}: Props) {
  const [minScore, setMinScore] = useState(0)
  const [remoteOnly, setRemoteOnly] = useState(false)
  const [textFilter, setTextFilter] = useState('')

  const visibleJobs = jobs.filter((job) => {
    if (job.score < minScore) return false
    if (remoteOnly && !job.remote) return false
    if (textFilter) {
      const haystack = `${job.title} ${job.company} ${job.location ?? ''}`.toLowerCase()
      if (!haystack.includes(textFilter.toLowerCase())) return false
    }
    return true
  })

  return (
    <section className="results">
      <div className="results-header">
        <div>
          <h2>
            {jobs.length > 0
              ? `${jobs.length} matching ${jobs.length === 1 ? 'job' : 'jobs'}`
              : 'No matching jobs found'}
          </h2>
          <p className="subtitle">
            Searched: {sourcesUsed.join(', ') || 'no sources'} &middot;{' '}
            {usedLlm ? 'scored by AI' : 'scored by keyword match'}
          </p>
        </div>
        <div className="results-actions">
          <button type="button" className="btn-secondary" onClick={onBackToProfile}>
            Edit profile
          </button>
          <button type="button" className="btn-secondary" onClick={onStartOver}>
            New CV
          </button>
        </div>
      </div>

      {sourcesFailed.length > 0 && (
        <p className="notice">
          Some job sources were unavailable and were skipped:{' '}
          {sourcesFailed.join(', ')}.
        </p>
      )}

      {jobs.length > 0 && (
        <div className="filter-row">
          <label className="filter-field">
            <span>Min score</span>
            <select
              value={minScore}
              onChange={(e) => setMinScore(Number(e.target.value))}
            >
              <option value={0}>Any</option>
              <option value={40}>40+</option>
              <option value={60}>60+</option>
              <option value={80}>80+</option>
            </select>
          </label>
          <label className="filter-field filter-checkbox">
            <input
              type="checkbox"
              checked={remoteOnly}
              onChange={(e) => setRemoteOnly(e.target.checked)}
            />
            <span>Remote only</span>
          </label>
          <input
            className="filter-text"
            placeholder="Filter by title, company, location…"
            value={textFilter}
            onChange={(e) => setTextFilter(e.target.value)}
          />
        </div>
      )}

      {jobs.length === 0 ? (
        <p className="empty-state">
          No jobs made the cut. Try moving the match scale towards
          &ldquo;similar roles&rdquo;, broadening your titles or skills, or
          removing the remote-only filter.
        </p>
      ) : visibleJobs.length === 0 ? (
        <p className="empty-state">No jobs match the current filters.</p>
      ) : (
        <div className="job-list">
          {visibleJobs.map((job) => (
            <JobCard key={job.id} job={job} />
          ))}
        </div>
      )}
    </section>
  )
}
