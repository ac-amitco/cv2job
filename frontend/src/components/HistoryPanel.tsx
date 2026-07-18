import type { HistoryEntry } from '../history'

interface Props {
  history: HistoryEntry[]
  onRestore: (entry: HistoryEntry) => void
  onClear: () => void
}

export default function HistoryPanel({ history, onRestore, onClear }: Props) {
  if (history.length === 0) return null
  return (
    <section className="history-panel">
      <div className="history-header">
        <h3>Recent searches</h3>
        <button type="button" className="link-button" onClick={onClear}>
          Clear
        </button>
      </div>
      <ul className="history-list">
        {history.map((entry) => (
          <li key={entry.ts}>
            <button
              type="button"
              className="history-item"
              onClick={() => onRestore(entry)}
            >
              <span className="history-title">
                {entry.profile.titles[0] ?? entry.profile.skills.slice(0, 3).join(', ')}
              </span>
              <span className="history-meta">
                {entry.jobs.length} jobs &middot;{' '}
                {new Date(entry.ts).toLocaleDateString()}{' '}
                {new Date(entry.ts).toLocaleTimeString([], {
                  hour: '2-digit',
                  minute: '2-digit',
                })}
              </span>
            </button>
          </li>
        ))}
      </ul>
    </section>
  )
}
