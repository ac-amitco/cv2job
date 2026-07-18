import type { LlmProvider } from '../types'

interface Props {
  providers: LlmProvider[]
  value: string
  onChange: (id: string) => void
}

export default function ModelSwitcher({ providers, value, onChange }: Props) {
  if (providers.length === 0) return null
  return (
    <label className="model-switcher">
      <span className="model-switcher-label">AI model</span>
      <select value={value} onChange={(e) => onChange(e.target.value)}>
        {providers.map((p) => (
          <option key={p.id} value={p.id} disabled={!p.available}>
            {p.label}
            {p.available ? '' : ' (key not configured)'}
          </option>
        ))}
      </select>
    </label>
  )
}
