import { useState } from 'react'
import {
  STATUS_LABELS,
  type TrackedJob,
  type TrackStatus,
} from '../tracker'

const COLUMNS: { title: string; statuses: TrackStatus[] }[] = [
  { title: 'Saved', statuses: ['saved'] },
  { title: 'Applied', statuses: ['applied'] },
  { title: 'Interview', statuses: ['interview'] },
  { title: 'Closed', statuses: ['offer', 'rejected'] },
]

interface CardProps {
  entry: TrackedJob
  onUpdate: (jobId: string, patch: { status?: TrackStatus; note?: string }) => void
  onRemove: (jobId: string) => void
}

function TrackerCard({ entry, onUpdate, onRemove }: CardProps) {
  const [note, setNote] = useState(entry.note)
  const { job } = entry

  return (
    <article className={`tracker-card status-border-${entry.status}`}>
      <div className="tracker-card-top">
        <a href={job.url} target="_blank" rel="noopener noreferrer">
          {job.title}
        </a>
        <button
          type="button"
          className="tracker-remove"
          title="Remove from tracker"
          onClick={() => onRemove(job.id)}
        >
          &times;
        </button>
      </div>
      <p className="tracker-company">
        {job.company}
        {job.score > 0 && <span className="tracker-score">{job.score}</span>}
      </p>
      <p className="tracker-dates">
        {entry.appliedAt
          ? `Applied ${new Date(entry.appliedAt).toLocaleDateString()}`
          : `Added ${new Date(entry.addedAt).toLocaleDateString()}`}
      </p>
      <select
        className="tracker-status"
        value={entry.status}
        onChange={(e) => onUpdate(job.id, { status: e.target.value as TrackStatus })}
      >
        {(Object.keys(STATUS_LABELS) as TrackStatus[]).map((s) => (
          <option key={s} value={s}>
            {STATUS_LABELS[s]}
          </option>
        ))}
      </select>
      <textarea
        className="tracker-note"
        placeholder="Add a note — contact, follow-up date…"
        value={note}
        rows={2}
        onChange={(e) => setNote(e.target.value)}
        onBlur={() => {
          if (note !== entry.note) onUpdate(job.id, { note })
        }}
      />
    </article>
  )
}

interface Props {
  tracked: TrackedJob[]
  onUpdate: (jobId: string, patch: { status?: TrackStatus; note?: string }) => void
  onRemove: (jobId: string) => void
  onClose: () => void
}

export default function TrackerBoard({ tracked, onUpdate, onRemove, onClose }: Props) {
  return (
    <section className="tracker-view">
      <div className="results-header">
        <div>
          <h2>Application tracker</h2>
          <p className="subtitle">
            {tracked.length > 0
              ? `${tracked.length} ${tracked.length === 1 ? 'job' : 'jobs'} tracked — stored in your browser.`
              : 'Jobs you save or apply to will appear here.'}
          </p>
        </div>
        <div className="results-actions">
          <button type="button" className="btn-secondary" onClick={onClose}>
            Back
          </button>
        </div>
      </div>

      {tracked.length === 0 ? (
        <p className="empty-state">
          Nothing tracked yet. Run a search and use ☆ Save or ✓ Applied on a
          job card to start your pipeline.
        </p>
      ) : (
        <div className="tracker-board">
          {COLUMNS.map((col) => {
            const entries = tracked.filter((e) => col.statuses.includes(e.status))
            return (
              <div key={col.title} className="tracker-col">
                <h3>
                  {col.title} <span>{entries.length}</span>
                </h3>
                {entries.map((entry) => (
                  <TrackerCard
                    key={entry.job.id}
                    entry={entry}
                    onUpdate={onUpdate}
                    onRemove={onRemove}
                  />
                ))}
              </div>
            )
          })}
        </div>
      )}
    </section>
  )
}
