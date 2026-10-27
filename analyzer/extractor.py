from typing import Protocol

from analyzer.models import Vacancy

MODEL = "claude-haiku-5-5"

SYSTEM_PROMPT = """You extract structured data from job postings for a job seeker.
Rules:
- Only report what the posting actually says. Do not guess missing values; use null or an empty list.
- Name skills with short canonical names ("Python", "AutoCAD", "Excel"), one skill per item.
- If a requirement means the same as one of the candidate's known skills, use exactly that known name,
  so the names can be compared directly.
- Convert salary to monthly USD only if the posting states a salary; otherwise null."""


class MessagesClient(Protocol):
    """The one SDK method we use. Lets tests pass a fake instead of a real Anthropic client."""

    def parse(self, **kwargs): ...


class VacancyExtractor:
    """Turns raw posting text into a Vacancy using Claude structured outputs."""

    def __init__(self, messages: MessagesClient, known_skills: list[str]) -> None:
        self._messages = messages
        self._known_skills = known_skills

    def extract(self, posting_text: str) -> Vacancy:
        if not posting_text.strip():
            raise ValueError("posting text is empty")

        response = self._messages.parse(
            model=MODEL,
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": self._build_prompt(posting_text)}],
            output_format=Vacancy,
        )
        return response.parsed_output

    def _build_prompt(self, posting_text: str) -> str:
        return (
            f"Candidate's known skills: {', '.join(self._known_skills)}\n\n"
            f"<posting>\n{posting_text}\n</posting>"
        )
