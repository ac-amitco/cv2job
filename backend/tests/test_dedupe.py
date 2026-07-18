from app.schemas import Job
from app.services.dedupe import dedupe


def make_job(id: str, title: str, company: str, description: str = "", **kwargs) -> Job:
    return Job(
        id=id,
        title=title,
        company=company,
        description=description,
        url="https://example.com",
        source=id.split(":")[0],
        **kwargs,
    )


def test_exact_duplicates_keep_richer_entry():
    short = make_job("remotive:1", "Python Developer", "Acme", "short")
    rich = make_job("adzuna:2", "Python Developer", "Acme", "a much longer description")
    result = dedupe([short, rich])
    assert len(result) == 1
    assert result[0].id == "adzuna:2"


def test_exact_key_ignores_case_and_punctuation():
    a = make_job("remotive:1", "Senior Engineer (Backend)", "Acme Inc.")
    b = make_job("arbeitnow:2", "senior engineer backend", "acme inc")
    assert len(dedupe([a, b])) == 1


def test_fuzzy_title_match_within_same_company():
    a = make_job("remotive:1", "Senior Backend Engineer", "Acme", "x" * 100)
    b = make_job("arbeitnow:2", "Backend Engineer Senior", "Acme", "y" * 10)
    result = dedupe([a, b])
    assert len(result) == 1
    assert result[0].id == "remotive:1"  # richer description wins


def test_same_title_different_companies_are_kept():
    a = make_job("remotive:1", "Python Developer", "Acme")
    b = make_job("remotive:2", "Python Developer", "Globex")
    assert len(dedupe([a, b])) == 2


def test_different_roles_at_same_company_are_kept():
    a = make_job("remotive:1", "Backend Engineer", "Acme")
    b = make_job("remotive:2", "Product Designer", "Acme")
    assert len(dedupe([a, b])) == 2
