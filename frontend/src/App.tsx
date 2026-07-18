import { useEffect, useState } from 'react'
import { getProviders, matchJobs, parseCv } from './api/client'
import { clearHistory, loadHistory, saveRun, type HistoryEntry } from './history'
import LoadingState from './components/LoadingState'
import ModelSwitcher from './components/ModelSwitcher'
import ProfileReview from './components/ProfileReview'
import ResultsList from './components/ResultsList'
import UploadScreen from './components/UploadScreen'
import type { CVProfile, MatchedJob, ProvidersResponse } from './types'

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

const MODEL_STORAGE_KEY = 'cv2job.model'

export default function App() {
  const [step, setStep] = useState<Step>({ step: 'upload' })
  const [providers, setProviders] = useState<ProvidersResponse | null>(null)
  const [model, setModel] = useState<string>(
    () => localStorage.getItem(MODEL_STORAGE_KEY) ?? '',
  )
  const [history, setHistory] = useState<HistoryEntry[]>(loadHistory)

  useEffect(() => {
    getProviders()
      .then((p) => {
        setProviders(p)
        const chosen = p.llm.find((m) => m.id === model && m.available)
        if (!chosen) {
          const fallback =
            p.llm.find((m) => m.default && m.available) ??
            p.llm.find((m) => m.available) ??
            p.llm.find((m) => m.default)
          if (fallback) setModel(fallback.id)
        }
      })
      .catch(() => setProviders(null))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    if (model) localStorage.setItem(MODEL_STORAGE_KEY, model)
  }, [model])

  const llmAvailable = providers?.llm.some((m) => m.available) ?? false

  async function handleFile(file: File) {
    setStep({ step: 'parsing' })
    try {
      const resp = await parseCv(file, model)
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
    usedLlm: boolean,
  ) {
    setStep({ step: 'searching', profile, usedLlm })
    try {
      const resp = await matchJobs({
        profile,
        model,
        location: location.trim() || null,
        remote_only: remoteOnly,
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
            cv2job
            <span className="brand-tagline">CV in, opportunities out</span>
          </h1>
          {providers && (
            <ModelSwitcher
              providers={providers.llm}
              value={model}
              onChange={setModel}
            />
          )}
        </div>
      </header>

      <main className="app-main">
        {step.step === 'upload' && (
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

        {step.step === 'parsing' && (
          <LoadingState
            message="Reading your CV…"
            detail="Extracting your skills, titles and experience"
          />
        )}

        {step.step === 'review' && (
          <ProfileReview
            initial={step.profile}
            usedLlm={step.usedLlm}
            onSearch={(profile, location, remoteOnly) =>
              handleSearch(profile, location, remoteOnly, step.usedLlm)
            }
            onBack={() => setStep({ step: 'upload' })}
          />
        )}

        {step.step === 'searching' && (
          <LoadingState
            message="Searching job boards…"
            detail="Querying live sources and scoring matches against your profile"
          />
        )}

        {step.step === 'results' && (
          <ResultsList
            jobs={step.jobs}
            sourcesUsed={step.sourcesUsed}
            sourcesFailed={step.sourcesFailed}
            usedLlm={step.matchedWithLlm}
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

        {step.step === 'error' && (
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
