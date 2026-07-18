from typing import Literal

from pydantic import BaseModel, Field


class CVProfile(BaseModel):
    name: str | None = None
    titles: list[str] = []
    skills: list[str] = []
    experience_years: float | None = None
    seniority: Literal["junior", "mid", "senior", "lead", "unknown"] = "unknown"
    locations: list[str] = []
    languages: list[str] = []
    summary: str = ""


class Job(BaseModel):
    id: str
    title: str
    company: str
    location: str | None = None
    remote: bool | None = None
    description: str = ""
    url: str
    source: str
    posted_at: str | None = None
    salary: str | None = None


class MatchedJob(Job):
    score: int = Field(ge=0, le=100)
    why: str


class ParseResponse(BaseModel):
    profile: CVProfile
    raw_text_chars: int
    used_llm: bool


class MatchRequest(BaseModel):
    profile: CVProfile
    model: str = "gemini"
    location: str | None = None
    remote_only: bool = False
    limit: int = Field(default=30, ge=1, le=100)


class MatchResponse(BaseModel):
    jobs: list[MatchedJob]
    sources_used: list[str]
    sources_failed: list[str]
    used_llm: bool
