import { useState, type CSSProperties } from 'react'
import { STATUS_LABELS, type TrackStatus } from '../tracker'
import type { MatchedJob } from '../types'

function scoreClass(score: number): string {
  if (score >= 80) return 'score-high'
  if (score >= 60) return 'score-mid'
  return 'score-low'
}

interface Props {
  job: MatchedJob
  trackedStatus?: TrackStatus
  onTrack: (job: MatchedJob, status: TrackStatus) => void
}

export default function JobCard({ job, trackedStatus, onTrack }: Props) {
  const [showNudge, setShowNudge] = useState(false)

  return (
    <article className="job-card card">
      <div className="job-card-header">
        <div>
          <h3 className="job-title">{job.title}</h3>
          <p className="job-company">{job.company}</p>
        </div>
        <span
          className={`score-ring ${scoreClass(job.score)}`}
          style={{ '--score': job.score } as CSSProperties}
          title={`Match score: ${job.score}/100`}
        >
          <span className="score-ring-inner">{job.score}</span>
        </span>
      </div>

      <p className="job-meta">
        {job.location && <span>{job.location}</span>}
        {job.remote && <span className="tag tag-remote">Remote</span>}
        {job.salary && <span>{job.salary}</span>}
        {job.posted_at && <span>Posted {job.posted_at.slice(0, 10)}</span>}
        <span className="tag tag-source">{job.source}</span>
        {trackedStatus && (
          <span className={`tag tag-status tag-status-${trackedStatus}`}>
            {STATUS_LABELS[trackedStatus]}
          </span>
        )}
      </p>

      <p className="job-why">{job.why}</p>

      <div className="job-card-footer">
        <a
          className="btn-primary btn-apply"
          href={job.url}
          target="_blank"
          rel="noopener noreferrer"
          onClick={() => {
            if (trackedStatus !== 'applied') setShowNudge(true)
          }}
        >
          Apply &rarr;
        </a>
        {trackedStatus === undefined && (
          <>
            <button
              type="button"
              className="btn-ghost"
              onClick={() => onTrack(job, 'saved')}
            >
              ☆ Save
            </button>
            <button
              type="button"
              className="btn-ghost"
              onClick={() => onTrack(job, 'applied')}
            >
              ✓ Applied
            </button>
          </>
        )}
        {trackedStatus === 'saved' && (
          <button
            type="button"
            className="btn-ghost"
            onClick={() => onTrack(job, 'applied')}
          >
            ✓ Mark applied
          </button>
        )}
        {showNudge && trackedStatus !== 'applied' && (
          <span className="apply-nudge">
            Did you apply?
            <button
              type="button"
              className="btn-ghost"
              onClick={() => {
                onTrack(job, 'applied')
                setShowNudge(false)
              }}
            >
              Yes, track it
            </button>
            <button
              type="button"
              className="nudge-dismiss"
              aria-label="Dismiss"
              onClick={() => setShowNudge(false)}
            >
              &times;
            </button>
          </span>
        )}
      </div>
    </article>
  )
}
