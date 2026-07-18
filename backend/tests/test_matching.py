from app.schemas import CVProfile, Job
from app.services.matching import build_query, lexical_score
from app.services.profile import build_profile_lexical

PROFILE = CVProfile(
    titles=["Python Developer"],
    skills=["python", "fastapi", "docker"],
    seniority="mid",
    summary="Backend developer",
)


def make_job(title: str, description: str) -> Job:
    return Job(
        id="test:1",
        title=title,
        company="Acme",
        description=description,
        url="https://example.com",
        source="test",
    )


def test_title_hit_outranks_skill_only_hit():
    title_hit = make_job("Senior Python Developer", "generic description")
    skill_hit = make_job("Data Analyst", "uses python and fastapi daily")
    title_score, _ = lexical_score(PROFILE, title_hit, remote_only=False)
    skill_score, _ = lexical_score(PROFILE, skill_hit, remote_only=False)
    assert title_score > skill_score


def test_matched_terms_are_reported():
    job = make_job("Python Developer", "We use fastapi and docker.")
    score, terms = lexical_score(PROFILE, job, remote_only=False)
    assert score > 0
    assert set(terms) == {"Python Developer", "python", "fastapi", "docker"}


def test_no_overlap_scores_zero():
    job = make_job("Pastry Chef", "Baking croissants all day")
    score, terms = lexical_score(PROFILE, job, remote_only=False)
    assert score == 0
    assert terms == []


def test_empty_profile_scores_zero():
    empty = CVProfile()
    job = make_job("Python Developer", "python")
    assert lexical_score(empty, job, remote_only=False) == (0.0, [])


def test_build_query_prefers_title_then_skills():
    assert build_query(PROFILE) == "Python Developer"
    assert build_query(CVProfile(skills=["go", "sql"])) == "go sql"
    assert build_query(CVProfile()) == "software developer"


def test_lexical_profile_extraction():
    text = (
        "Jane Doe\nSenior Backend Developer with 7 years of experience.\n"
        "Skills: Python, FastAPI, Docker, AWS, PostgreSQL.\n"
        "Languages: English, Hebrew.\n"
    ) * 5  # pad past the minimum-length heuristics
    profile = build_profile_lexical(text)
    assert "python" in profile.skills
    assert profile.seniority == "senior"
    assert profile.experience_years == 7.0
    assert "English" in profile.languages
    assert any("Backend Developer" in t for t in profile.titles)
