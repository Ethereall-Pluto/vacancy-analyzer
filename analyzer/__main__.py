import argparse
import os
import sys
from pathlib import Path

from anthropic import Anthropic

from analyzer.extractor import VacancyExtractor
from analyzer.matcher import match
from analyzer.models import Profile
from analyzer.report import format_report


def main() -> None:
    parser = argparse.ArgumentParser(description="Check how well a job posting fits your profile.")
    parser.add_argument("posting", type=Path, help="Text file with the job posting")
    parser.add_argument("--profile", type=Path, required=True, help="JSON file with your skills")
    args = parser.parse_args()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("Set the ANTHROPIC_API_KEY environment variable first.")

    profile = Profile.model_validate_json(args.profile.read_text(encoding="utf-8"))
    posting_text = args.posting.read_text(encoding="utf-8")

    extractor = VacancyExtractor(Anthropic().messages, known_skills=profile.skills)
    vacancy = extractor.extract(posting_text)
    print(format_report(vacancy, match(vacancy, profile, posting_text)))


if __name__ == "__main__":
    main()
