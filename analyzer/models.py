from pydantic import BaseModel, Field


class Vacancy(BaseModel):
    """What Claude extracts from a job posting. The schema is also what the model is forced to return."""

    title: str
    company: str | None = Field(description="Company name, or null if not stated")
    seniority: str | None = Field(description="Trainee, Junior, Middle, Senior, or null if not stated")
    required_skills: list[str] = Field(description="Skills the posting calls mandatory")
    nice_to_have: list[str] = Field(description="Skills listed as a plus or optional")
    salary_min_usd: int | None = Field(description="Lower bound of monthly salary in USD, or null")
    salary_max_usd: int | None = Field(description="Upper bound of monthly salary in USD, or null")
    remote: bool | None = Field(description="True if fully remote, false if office/hybrid, null if unclear")
    red_flags: list[str] = Field(
        description="Concrete warning signs: unpaid test tasks, vague duties, one person for several roles, "
        "unrealistic stack for the level, no salary info. Empty list if none."
    )


class Profile(BaseModel):
    """The candidate side: what I can do and what I refuse to do."""

    skills: list[str] = Field(min_length=1)
    stop_keywords: list[str] = []
    min_salary_usd: int | None = None


class MatchResult(BaseModel):
    matched: list[str]
    missing: list[str]
    bonus: list[str]
    score: int
    stop_keywords_found: list[str]
    salary_below_minimum: bool
