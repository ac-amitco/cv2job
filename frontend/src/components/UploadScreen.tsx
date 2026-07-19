import { useRef, useState } from 'react'
import type { HistoryEntry } from '../history'
import HistoryPanel from './HistoryPanel'

const MAX_FILE_BYTES = 5 * 1024 * 1024
const ACCEPTED = ['.pdf', '.docx']

interface Props {
  onFile: (file: File) => void
  llmAvailable: boolean
  history: HistoryEntry[]
  onRestoreHistory: (entry: HistoryEntry) => void
  onClearHistory: () => void
}

export default function UploadScreen({
  onFile,
  llmAvailable,
  history,
  onRestoreHistory,
  onClearHistory,
}: Props) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [dragOver, setDragOver] = useState(false)
  const [validationError, setValidationError] = useState<string | null>(null)

  function handleFile(file: File | undefined) {
    if (!file) return
    const ext = '.' + (file.name.split('.').pop() ?? '').toLowerCase()
    if (!ACCEPTED.includes(ext)) {
      setValidationError('Please upload a PDF or DOCX file.')
      return
    }
    if (file.size > MAX_FILE_BYTES) {
      setValidationError('File is larger than 5 MB — please upload a smaller CV.')
      return
    }
    setValidationError(null)
    onFile(file)
  }

  return (
    <section className="upload-screen">
      <h2 className="hero-title">
        Your CV, turned into
        <br />
        <em>real opportunities</em>
      </h2>
      <p className="subtitle hero-subtitle">
        Upload your CV and we&apos;ll search live job boards for openings that
        fit your skills and experience — with a direct link to apply.
      </p>

      <div
        className={`dropzone${dragOver ? ' dropzone-active' : ''}`}
        onClick={() => inputRef.current?.click()}
        onDragOver={(e) => {
          e.preventDefault()
          setDragOver(true)
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => {
          e.preventDefault()
          setDragOver(false)
          handleFile(e.dataTransfer.files[0])
        }}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') inputRef.current?.click()
        }}
      >
        <div className="dropzone-icon" aria-hidden>
          &#8613;
        </div>
        <strong>Drop your CV here</strong>
        <span>PDF or DOCX, up to 5 MB</span>
        <span className="dropzone-cta">Browse files</span>
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.docx"
          hidden
          onChange={(e) => handleFile(e.target.files?.[0])}
        />
      </div>

      {validationError && <p className="form-error">{validationError}</p>}

      <ul className="feature-strip" aria-label="How it works">
        <li>
          <strong>1 · AI reads your CV</strong>
          <span>Skills, titles and experience, extracted in seconds</span>
        </li>
        <li>
          <strong>2 · Live job search</strong>
          <span>Openings from four job boards, deduplicated</span>
        </li>
        <li>
          <strong>3 · Scored for you</strong>
          <span>Each job rated 0–100 with a why-it-fits note</span>
        </li>
      </ul>

      {!llmAvailable && (
        <p className="notice">
          No AI provider is configured on the server, so profile extraction and
          matching will use keyword analysis. Add a free Gemini API key to{' '}
          <code>backend/.env</code> for full AI matching.
        </p>
      )}

      <HistoryPanel
        history={history}
        onRestore={onRestoreHistory}
        onClear={onClearHistory}
      />
    </section>
  )
}
