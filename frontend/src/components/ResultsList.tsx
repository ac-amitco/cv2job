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

      {jobs.length === 0 ? (
        <p className="empty-state">
          Try broadening your titles or skills, or removing the remote-only
          filter.
        </p>
      ) : (
        <div className="job-list">
          {jobs.map((job) => (
            <JobCard key={job.id} job={job} />
          ))}
        </div>
      )}
    </section>
  )
}
