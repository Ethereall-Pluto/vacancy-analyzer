# Vacancy Analyzer

A command-line tool that reads a job posting, extracts its requirements with the Claude API,
and checks them against your skills profile: match score, missing skills, salary, red flags
and stop keywords.

I built it to speed up my own job search — instead of re-reading every posting,
I get a short report and decide whether it's worth applying.

**Stack:** Python, Anthropic SDK (structured outputs), Pydantic, pytest.

## How it works

```
posting.txt ──► VacancyExtractor ──► Vacancy ──► match() ──► MatchResult ──► format_report()
                (Claude API)        (Pydantic)   (plain code)
```

| Module | Responsibility |
|---|---|
| `models.py` | Pydantic models. `Vacancy` doubles as the JSON schema Claude must return. |
| `extractor.py` | `VacancyExtractor` — the only code that calls the API. Uses `messages.parse` with structured outputs, so the response is always a valid `Vacancy`. |
| `matcher.py` | Pure comparison logic: skills, score, salary, stop keywords. No AI, no I/O. |
| `report.py` | Turns the result into readable text. |

Design decisions:

- **AI extracts, code decides.** The model only turns free text into structured data. Scoring and filtering are deterministic Python, so the same input always gives the same verdict and the rules are unit-tested.
- **Structured outputs instead of "please answer in JSON".** The schema is enforced by the API, so there's no fragile parsing of model text.
- **Shared skill vocabulary.** The prompt includes the candidate's skill names and asks the model to reuse them, so "Python 3.x scripting" comes back as `Python` and matches directly.
- **The API client is injected.** Tests pass a fake object with the same `parse` method, so the test suite runs offline, for free, in milliseconds.
- **Stop keywords are checked in the raw text**, not in what the model extracted, so a model omission can't hide them.

## Run

```bash
pip install anthropic pydantic
export ANTHROPIC_API_KEY=...
python -m analyzer examples/posting.txt --profile examples/profile.json
```

Edit `examples/profile.json` with your own skills, stop keywords and minimum salary.

Example report format (for the sample posting in `examples/`):

```
Junior CAD Drafter (Electrical)
Seniority: Junior | Remote: yes | Salary: $700–900

Match score: 50%
  Have:     AutoCAD, English
  Missing:  Revit, Electrical Schematics
  Bonus:    Python

Warnings:
  - Unpaid test task of 4-6 hours
```

## Tests

```bash
pip install pytest
pytest
```

Requires Python 3.10+.
