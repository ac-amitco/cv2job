import re
from collections import Counter

from ..schemas import CVProfile

# Keyword fallback used when no LLM provider is configured. Deliberately small
# and common — the LLM path (when available) replaces this entirely.
KNOWN_SKILLS = [
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
    "ruby", "php", "swift", "kotlin", "scala", "sql", "html", "css",
    "react", "angular", "vue", "next.js", "node.js", "django", "flask",
    "fastapi", "spring", ".net", "rails", "express",
    "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "linux",
    "git", "ci/cd", "jenkins", "graphql", "rest", "microservices",
    "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "kafka",
    "machine learning", "deep learning", "pytorch", "tensorflow", "pandas",
    "numpy", "data analysis", "nlp", "computer vision", "etl", "spark",
    "excel", "tableau", "power bi", "figma", "photoshop",
    "agile", "scrum", "jira", "product management", "project management",
    "marketing", "seo", "sales", "customer support", "accounting", "hr",
    "qa", "selenium", "cypress", "automation", "android", "ios",
]

_TITLE_RE = re.compile(
    r"\b(senior|junior|lead|principal|staff)?\s*"
    r"(software|backend|back[- ]end|frontend|front[- ]end|full[- ]?stack|web|mobile|"
    r"data|devops|cloud|security|machine learning|ml|ai|qa|automation|embedded|"
    r"product|project|program|marketing|sales|ux|ui)?\s*"
    r"(engineer|developer|scientist|analyst|architect|manager|designer|consultant|"
    r"administrator|specialist|lead)\b",
    re.IGNORECASE,
)

_YEARS_RE = re.compile(r"(\d{1,2})\s*\+?\s*years?", re.IGNORECASE)

KNOWN_LANGUAGES = [
    "english", "hebrew", "spanish", "french", "german", "russian", "arabic",
    "portuguese", "italian", "dutch", "chinese", "mandarin", "japanese", "hindi",
]


def build_profile_lexical(text: str) -> CVProfile:
    """Heuristic profile extraction — fallback when no LLM key is configured."""
    lower = text.lower()

    skills = [s for s in KNOWN_SKILLS if s in lower][:20]

    title_counts: Counter[str] = Counter()
    for match in _TITLE_RE.finditer(text):
        title = " ".join(part for part in match.groups() if part)
        title = re.sub(r"\s+", " ", title).strip().title()
        if len(title.split()) >= 2:
            title_counts[title] += 1
    titles = [t for t, _ in title_counts.most_common(3)]

    if re.search(r"\b(principal|staff|lead)\b", lower):
        seniority = "lead"
    elif "senior" in lower:
        seniority = "senior"
    elif re.search(r"\b(junior|intern|internship|graduate)\b", lower):
        seniority = "junior"
    else:
        seniority = "unknown"

    years = [int(m.group(1)) for m in _YEARS_RE.finditer(text) if int(m.group(1)) <= 40]
    experience_years = float(max(years)) if years else None

    languages = [lang.title() for lang in KNOWN_LANGUAGES if lang in lower]

    summary_bits = []
    if titles:
        summary_bits.append(f"Candidate profile: {titles[0]}")
    if skills:
        summary_bits.append(f"key skills: {', '.join(skills[:8])}")
    summary = "; ".join(summary_bits) or "Profile extracted by keyword matching."

    return CVProfile(
        name=None,
        titles=titles,
        skills=skills,
        experience_years=experience_years,
        seniority=seniority,
        locations=[],
        languages=languages,
        summary=summary,
    )
