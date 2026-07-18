export type Seniority = 'junior' | 'mid' | 'senior' | 'lead' | 'unknown'

export interface CVProfile {
  name: string | null
  titles: string[]
  skills: string[]
  experience_years: number | null
  seniority: Seniority
  locations: string[]
  languages: string[]
  summary: string
}

export interface MatchedJob {
  id: string
  title: string
  company: string
  location: string | null
  remote: boolean | null
  description: string
  url: string
  source: string
  posted_at: string | null
  salary: string | null
  score: number
  why: string
}

export interface LlmProvider {
  id: string
  label: string
  model: string
  available: boolean
  default: boolean
}

export interface JobSourceInfo {
  id: string
  available: boolean
}

export interface ProvidersResponse {
  llm: LlmProvider[]
  job_sources: JobSourceInfo[]
}

export interface ParseResponse {
  profile: CVProfile
  raw_text_chars: number
  used_llm: boolean
}

export interface MatchRequest {
  profile: CVProfile
  model: string
  location?: string | null
  remote_only?: boolean
  limit?: number
}

export interface MatchResponse {
  jobs: MatchedJob[]
  sources_used: string[]
  sources_failed: string[]
  used_llm: boolean
}
