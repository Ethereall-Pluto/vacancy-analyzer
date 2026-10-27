from analyzer.models import MatchResult, Profile, Vacancy


def match(vacancy: Vacancy, profile: Profile, posting_text: str) -> MatchResult:
    """Compare a vacancy with the profile. Pure and deterministic: the AI extracts, plain code decides."""
    have = {skill.lower() for skill in profile.skills}

    matched = [s for s in vacancy.required_skills if s.lower() in have]
    missing = [s for s in vacancy.required_skills if s.lower() not in have]
    bonus = [s for s in vacancy.nice_to_have if s.lower() in have]

    return MatchResult(
        matched=matched,
        missing=missing,
        bonus=bonus,
        score=_score(len(matched), len(vacancy.required_skills)),
        stop_keywords_found=_stop_keywords_in(posting_text, profile.stop_keywords),
        salary_below_minimum=_salary_below_minimum(vacancy, profile),
    )


def _score(matched: int, required: int) -> int:
    """Share of mandatory skills covered, 0-100. A posting with no mandatory skills blocks nothing."""
    if required == 0:
        return 100
    return round(100 * matched / required)


def _stop_keywords_in(posting_text: str, stop_keywords: list[str]) -> list[str]:
    text = posting_text.lower()
    return [word for word in stop_keywords if word.lower() in text]


def _salary_below_minimum(vacancy: Vacancy, profile: Profile) -> bool:
    """True only when the posting's best offer is known and still under the minimum."""
    if profile.min_salary_usd is None:
        return False
    best_offer = vacancy.salary_max_usd or vacancy.salary_min_usd
    return best_offer is not None and best_offer < profile.min_salary_usd
