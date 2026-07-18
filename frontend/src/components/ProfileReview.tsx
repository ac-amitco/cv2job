import { useState } from 'react'
import type { CVProfile, Seniority } from '../types'
import ChipList from './ChipList'

const SENIORITIES: Seniority[] = ['junior', 'mid', 'senior', 'lead', 'unknown']

interface Props {
  initial: CVProfile
  usedLlm: boolean
  onSearch: (profile: CVProfile, location: string, remoteOnly: boolean) => void
  onBack: () => void
}

export default function ProfileReview({ initial, usedLlm, onSearch, onBack }: Props) {
  const [profile, setProfile] = useState<CVProfile>(initial)
  const [location, setLocation] = useState(initial.locations[0] ?? '')
  const [remoteOnly, setRemoteOnly] = useState(false)

  return (
    <section className="profile-review">
      <h2>Review your profile</h2>
      <p className="subtitle">
        {usedLlm
          ? 'This is what the AI extracted from your CV. Adjust anything before we search.'
          : 'Extracted by keyword analysis (no AI key configured). Please review and complete it before we search.'}
      </p>

      <div className="card">
        <ChipList
          label="Job titles to search for"
          items={profile.titles}
          onChange={(titles) => setProfile({ ...profile, titles })}
          placeholder="e.g. Backend Developer"
        />
        <ChipList
          label="Skills"
          items={profile.skills}
          onChange={(skills) => setProfile({ ...profile, skills })}
          placeholder="e.g. Python"
        />

        <div className="field-row">
          <label className="field">
            <span className="field-label">Preferred location</span>
            <input
              value={location}
              placeholder="e.g. Tel Aviv, London, US…"
              onChange={(e) => setLocation(e.target.value)}
            />
          </label>
          <label className="field">
            <span className="field-label">Seniority</span>
            <select
              value={profile.seniority}
              onChange={(e) =>
                setProfile({ ...profile, seniority: e.target.value as Seniority })
              }
            >
              {SENIORITIES.map((s) => (
                <option key={s} value={s}>
                  {s === 'unknown' ? 'not specified' : s}
                </option>
              ))}
            </select>
          </label>
          <label className="field checkbox-field">
            <input
              type="checkbox"
              checked={remoteOnly}
              onChange={(e) => setRemoteOnly(e.target.checked)}
            />
            <span>Remote only</span>
          </label>
        </div>
      </div>

      <div className="actions">
        <button type="button" className="btn-secondary" onClick={onBack}>
          Upload a different CV
        </button>
        <button
          type="button"
          className="btn-primary"
          disabled={profile.titles.length === 0 && profile.skills.length === 0}
          onClick={() => onSearch(profile, location, remoteOnly)}
        >
          Find matching jobs
        </button>
      </div>
    </section>
  )
}
