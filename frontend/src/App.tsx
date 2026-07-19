import { useEffect, useState } from 'react'
import { getProviders, matchJobs, parseCv } from './api/client'
import { clearHistory, loadHistory, saveRun, type HistoryEntry } from './history'
import {
  loadTracker,
  removeTracked,
  trackJob,
  updateTracked,
  type TrackedJob,
  type TrackStatus,
} from './tracker'
import LoadingState from './components/LoadingState'
import ProfileReview from './components/ProfileReview'
import ResultsList from './components/ResultsList'
import StepIndicator from './components/StepIndicator'
import TrackerBoard from './components/TrackerBoard'
import UploadScreen from './components/UploadScreen'
import type { CVProfile, MatchedJob } from './types'

type Step =
  | { step: 'upload' }
  | { step: 'parsing' }
  | { step: 'review'; profile: CVProfile; usedLlm: boolean }
  | { step: 'searching'; profile: CVProfile; usedLlm: boolean }
  | {
      step: 'results'
      profile: CVProfile
      usedLlm: boolean
      jobs: MatchedJob[]
      sourcesUsed: string[]
      sourcesFailed: string[]
      matchedWithLlm: boolean
    }
  | { step: 'error'; message: string; back: Step }

const STEP_STAGE: Record<Step['step'], number> = {
  upload: 0,
  parsing: 0,
  review: 1,
  searching: 1,
  results: 2,
  error: 0,
}

export default function App() {
  const [step, setStep] = useState<Step>({ step: 'upload' })
  const [llmAvailable, setLlmAvailable] = useState(true)
  const [history, setHistory] = useState<HistoryEntry[]>(loadHistory)
  const [tracked, setTracked] = useState<TrackedJob[]>(loadTracker)
  const [trackerOpen, setTrackerOpen] = useState(false)

  const trackedStatuses = new Map<string, TrackStatus>(
    tracked.map((e) => [e.job.id, e.status]),
  )

  function handleTrack(job: MatchedJob, status: TrackStatus) {
    setTracked(trackJob(job, status))
  }

  useEffect(() => {
    getProviders()
      .then((p) => setLlmAvailable(p.llm.some((m) => m.available)))
      .catch(() => setLlmAvailable(false))
  }, [])

  async function handleFile(file: File) {
    setStep({ step: 'parsing' })
    try {
      const resp = await parseCv(file)
      setStep({ step: 'review', profile: resp.profile, usedLlm: resp.used_llm })
    } catch (err) {
      setStep({
        step: 'error',
        message: err instanceof Error ? err.message : 'Something went wrong.',
        back: { step: 'upload' },
      })
    }
  }

  async function handleSearch(
    profile: CVProfile,
    location: string,
    remoteOnly: boolean,
    flexibility: number,
    usedLlm: boolean,
  ) {
    setStep({ step: 'searching', profile, usedLlm })
    try {
      const resp = await matchJobs({
        profile,
        location: location.trim() || null,
        remote_only: remoteOnly,
        flexibility,
      })
      setStep({
        step: 'results',
        profile,
        usedLlm,
        jobs: resp.jobs,
        sourcesUsed: resp.sources_used,
        sourcesFailed: resp.sources_failed,
        matchedWithLlm: resp.used_llm,
      })
      setHistory(
        saveRun({
          ts: Date.now(),
          profile,
          jobs: resp.jobs,
          sourcesUsed: resp.sources_used,
          sourcesFailed: resp.sources_failed,
          usedLlm: resp.used_llm,
        }),
      )
    } catch (err) {
      setStep({
        step: 'error',
        message: err instanceof Error ? err.message : 'Something went wrong.',
        back: { step: 'review', profile, usedLlm },
      })
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="app-header-inner">
          <h1 className="brand">
            <span className="brand-mark" aria-hidden />
            cv2job
          </h1>
          <div className="header-right">
            <StepIndicator active={STEP_STAGE[step.step]} />
            <button
              type="button"
              className={`tracker-toggle${trackerOpen ? ' tracker-toggle-active' : ''}`}
              onClick={() => setTrackerOpen((open) => !open)}
            >
              Tracker
              {tracked.length > 0 && (
                <span className="tracker-count">{tracked.length}</span>
              )}
            </button>
          </div>
        </div>
      </header>

      <main className="app-main">
        {trackerOpen && (
          <TrackerBoard
            tracked={tracked}
            onUpdate={(jobId, patch) => setTracked(updateTracked(jobId, patch))}
            onRemove={(jobId) => setTracked(removeTracked(jobId))}
            onClose={() => setTrackerOpen(false)}
          />
        )}

        {!trackerOpen && step.step === 'upload' && (
          <UploadScreen
            onFile={handleFile}
            llmAvailable={llmAvailable}
            history={history}
            onRestoreHistory={(entry) =>
              setStep({
                step: 'results',
                profile: entry.profile,
                usedLlm: entry.usedLlm,
                jobs: entry.jobs,
                sourcesUsed: entry.sourcesUsed,
                sourcesFailed: entry.sourcesFailed,
                matchedWithLlm: entry.usedLlm,
              })
            }
            onClearHistory={() => {
              clearHistory()
              setHistory([])
            }}
          />
        )}

        {!trackerOpen && step.step === 'parsing' && (
          <LoadingState
            message="Reading your CV…"
            detail="Extracting your skills, titles and experience"
          />
        )}

        {!trackerOpen && step.step === 'review' && (
          <ProfileReview
            initial={step.profile}
            usedLlm={step.usedLlm}
            onSearch={(profile, location, remoteOnly, flexibility) =>
              handleSearch(profile, location, remoteOnly, flexibility, step.usedLlm)
            }
            onBack={() => setStep({ step: 'upload' })}
          />
        )}

        {!trackerOpen && step.step === 'searching' && (
          <LoadingState
            message="Searching job boards…"
            detail="Querying live sources and scoring matches against your profile"
          />
        )}

        {!trackerOpen && step.step === 'results' && (
          <ResultsList
            jobs={step.jobs}
            sourcesUsed={step.sourcesUsed}
            sourcesFailed={step.sourcesFailed}
            usedLlm={step.matchedWithLlm}
            trackedStatuses={trackedStatuses}
            onTrack={handleTrack}
            onBackToProfile={() =>
              setStep({
                step: 'review',
                profile: step.profile,
                usedLlm: step.usedLlm,
              })
            }
            onStartOver={() => setStep({ step: 'upload' })}
          />
        )}

        {!trackerOpen && step.step === 'error' && (
          <section className="error-state">
            <h2>Something went wrong</h2>
            <p>{step.message}</p>
            <button
              type="button"
              className="btn-primary"
              onClick={() => setStep(step.back)}
            >
              Try again
            </button>
          </section>
        )}
      </main>

      <footer className="app-footer">
        Job data from Remotive, Arbeitnow, Adzuna and JSearch. Your CV is
        processed in memory and never stored.
      </footer>
    </div>
  )
}
