import { useState } from 'react'

interface Props {
  label: string
  items: string[]
  onChange: (items: string[]) => void
  placeholder?: string
}

export default function ChipList({ label, items, onChange, placeholder }: Props) {
  const [draft, setDraft] = useState('')

  function add() {
    const value = draft.trim()
    if (!value) return
    if (!items.some((i) => i.toLowerCase() === value.toLowerCase())) {
      onChange([...items, value])
    }
    setDraft('')
  }

  return (
    <div className="chip-field">
      <span className="field-label">{label}</span>
      <div className="chip-list">
        {items.map((item) => (
          <span key={item} className="chip">
            {item}
            <button
              type="button"
              className="chip-remove"
              aria-label={`Remove ${item}`}
              onClick={() => onChange(items.filter((i) => i !== item))}
            >
              &times;
            </button>
          </span>
        ))}
        <input
          className="chip-input"
          value={draft}
          placeholder={placeholder ?? 'Add…'}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') {
              e.preventDefault()
              add()
            }
          }}
          onBlur={add}
        />
      </div>
    </div>
  )
}
