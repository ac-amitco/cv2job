import { useRef, useState } from 'react'

const MAX_FILE_BYTES = 5 * 1024 * 1024
const ACCEPTED = ['.pdf', '.docx']

interface Props {
  onFile: (file: File) => void
  llmAvailable: boolean
}

export default function UploadScreen({ onFile, llmAvailable }: Props) {
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
      <h2>Find jobs that match your CV</h2>
      <p className="subtitle">
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
          &#128196;
        </div>
        <strong>Drop your CV here</strong>
        <span>or click to browse — PDF or DOCX, up to 5 MB</span>
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.docx"
          hidden
          onChange={(e) => handleFile(e.target.files?.[0])}
        />
      </div>

      {validationError && <p className="form-error">{validationError}</p>}

      {!llmAvailable && (
        <p className="notice">
          No AI provider is configured on the server, so profile extraction and
          matching will use keyword analysis. Add a free Gemini API key to{' '}
          <code>backend/.env</code> for full AI matching.
        </p>
      )}
    </section>
  )
}
