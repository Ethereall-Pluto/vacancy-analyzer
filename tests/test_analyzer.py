from types import SimpleNamespace

import pytest

from analyzer.extractor import VacancyExtractor
from analyzer.matcher import match
from analyzer.models import Profile, Vacancy
from analyzer.report import format_report


def make_vacancy(**overrides) -> Vacancy:
    fields = dict(
        title="CAD Specialist",
        company="Acme",
        seniority="Junior",
        required_skills=["AutoCAD", "Revit", "English"],
        nice_to_have=["Python"],
        salary_min_usd=800,
        salary_max_usd=1000,
        remote=True,
        red_flags=[],
    )
    return Vacancy(**(fields | overrides))


PROFILE = Profile(skills=["autocad", "Python", "English"], stop_keywords=["cold calling"], min_salary_usd=900)


class FakeMessages:
    """Records the request and returns a canned Vacancy, like the SDK's messages.parse would."""

    def __init__(self, vacancy: Vacancy) -> None:
        self.vacancy = vacancy
        self.request: dict = {}

    def parse(self, **kwargs):
        self.request = kwargs
        return SimpleNamespace(parsed_output=self.vacancy)


def test_extractor_returns_parsed_vacancy_and_sends_known_skills():
    fake = FakeMessages(make_vacancy())
    extractor = VacancyExtractor(fake, known_skills=["AutoCAD", "Python"])

    vacancy = extractor.extract("We need a CAD specialist...")

    assert vacancy.title == "CAD Specialist"
    assert fake.request["output_format"] is Vacancy
    prompt = fake.request["messages"][0]["content"]
    assert "AutoCAD, Python" in prompt
    assert "We need a CAD specialist..." in prompt


def test_extractor_rejects_empty_posting():
    with pytest.raises(ValueError):
        VacancyExtractor(FakeMessages(make_vacancy()), known_skills=["Python"]).extract("   ")


def test_match_is_case_insensitive_and_scores_required_skills():
    result = match(make_vacancy(), PROFILE, posting_text="")

    assert result.matched == ["AutoCAD", "English"]
    assert result.missing == ["Revit"]
    assert result.bonus == ["Python"]
    assert result.score == 67


def test_no_required_skills_scores_full():
    assert match(make_vacancy(required_skills=[]), PROFILE, posting_text="").score == 100


def test_stop_keywords_are_found_in_raw_text():
    result = match(make_vacancy(), PROFILE, posting_text="Daily COLD CALLING to leads")
    assert result.stop_keywords_found == ["cold calling"]


@pytest.mark.parametrize(
    ("low", "high", "expected"),
    [(800, 1000, False), (500, 800, True), (None, None, False), (850, None, True)],
)
def test_salary_below_minimum(low, high, expected):
    vacancy = make_vacancy(salary_min_usd=low, salary_max_usd=high)
    assert match(vacancy, PROFILE, posting_text="").salary_below_minimum is expected


def test_report_lists_red_flags_and_salary_warning():
    vacancy = make_vacancy(salary_min_usd=300, salary_max_usd=None, red_flags=["Unpaid test task"])
    report = format_report(vacancy, match(vacancy, PROFILE, posting_text=""))

    assert "Match score: 67%" in report
    assert "Unpaid test task" in report
    assert "Salary is below your minimum" in report
