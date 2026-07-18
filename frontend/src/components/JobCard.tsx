import type { MatchedJob } from '../types'

function scoreClass(score: number): string {
  if (score >= 80) return 'score-high'
  if (score >= 60) return 'score-mid'
  return 'score-low'
}

export default function JobCard({ job }: { job: MatchedJob }) {
  return (
    <article className="job-card card">
      <div className="job-card-header">
        <div>
          <h3 className="job-title">{job.title}</h3>
          <p className="job-company">{job.company}</p>
        </div>
        <span
          className={`score-badge ${scoreClass(job.score)}`}
          title="Match score"
        >
          {job.score}
        </span>
      </div>

      <p className="job-meta">
        {job.location && <span>{job.location}</span>}
        {job.remote && <span className="tag tag-remote">Remote</span>}
        {job.salary && <span>{job.salary}</span>}
        {job.posted_at && <span>Posted {job.posted_at.slice(0, 10)}</span>}
        <span className="tag tag-source">{job.source}</span>
      </p>

      <p className="job-why">{job.why}</p>

      <div className="job-card-footer">
        <a
          className="btn-primary btn-apply"
          href={job.url}
          target="_blank"
          rel="noopener noreferrer"
        >
          Apply &rarr;
        </a>
      </div>
    </article>
  )
}
