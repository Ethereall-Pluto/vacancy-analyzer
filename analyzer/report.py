from analyzer.models import MatchResult, Vacancy


def format_report(vacancy: Vacancy, result: MatchResult) -> str:
    lines = [
        f"{vacancy.title}" + (f" — {vacancy.company}" if vacancy.company else ""),
        f"Seniority: {vacancy.seniority or 'not stated'} | Remote: {_yes_no(vacancy.remote)} | "
        f"Salary: {_salary(vacancy)}",
        "",
        f"Match score: {result.score}%",
        f"  Have:     {_join(result.matched)}",
        f"  Missing:  {_join(result.missing)}",
        f"  Bonus:    {_join(result.bonus)}",
    ]

    warnings = list(vacancy.red_flags)
    if result.stop_keywords_found:
        warnings.append(f"Stop keywords in posting: {', '.join(result.stop_keywords_found)}")
    if result.salary_below_minimum:
        warnings.append("Salary is below your minimum")

    lines += ["", "Warnings:"] + ([f"  - {w}" for w in warnings] or ["  none"])
    return "\n".join(lines)


def _join(items: list[str]) -> str:
    return ", ".join(items) or "—"


def _yes_no(value: bool | None) -> str:
    return {True: "yes", False: "no", None: "unclear"}[value]


def _salary(vacancy: Vacancy) -> str:
    low, high = vacancy.salary_min_usd, vacancy.salary_max_usd
    if low is None and high is None:
        return "not stated"
    if low is not None and high is not None:
        return f"${low}–{high}"
    return f"${low or high}"
