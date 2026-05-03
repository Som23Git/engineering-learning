import json
import re
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "docs"
DAILY_DIR = DOCS_DIR / "daily"
ROADMAP_FILE = ROOT / "roadmap.json"
DAILY_INDEX_FILE = DAILY_DIR / "index.md"
ROADMAP_DOC_FILE = DOCS_DIR / "roadmap.md"


def title_from_filename(path: Path) -> str:
    """
    Converts:
    2026-05-03-day-001-http-fundamentals.md

    To:
    Day 001 — HTTP Fundamentals
    """
    name = path.stem
    match = re.search(r"day-(\d{3})-(.+)$", name)

    if not match:
        return path.stem.replace("-", " ").title()

    day = match.group(1)
    topic = match.group(2).replace("-", " ").title()
    return f"Day {day} — {topic}"


def load_roadmap() -> List[Dict[str, Any]]:
    if not ROADMAP_FILE.exists():
        return []

    with open(ROADMAP_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def update_daily_index() -> None:
    DAILY_DIR.mkdir(parents=True, exist_ok=True)

    lessons = sorted(
        [
            path
            for path in DAILY_DIR.glob("*.md")
            if path.name != "index.md"
        ]
    )

    lines = [
        "# Daily Lessons",
        "",
        "This page is automatically updated by GitHub Actions.",
        "",
    ]

    if not lessons:
        lines.append("No lessons generated yet.")
    else:
        lines.append("## Lessons")
        lines.append("")

        for lesson in lessons:
            title = title_from_filename(lesson)
            lines.append(f"- [{title}]({lesson.name})")

    DAILY_INDEX_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_roadmap_doc() -> None:
    roadmap = load_roadmap()

    lines = [
        "# Engineering Learning Roadmap",
        "",
        "This roadmap is the source of truth for the daily learning automation.",
        "",
    ]

    if not roadmap:
        lines.append("No roadmap items found.")
        ROADMAP_DOC_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return

    current_phase = None

    for item in roadmap:
        phase = item.get("phase", "Uncategorized")
        day = item.get("day", "")
        topic = item.get("topic", "Untitled")
        category = item.get("category", "")
        difficulty = item.get("difficulty", "")
        objective = item.get("learning_objective", "")

        if phase != current_phase:
            lines.append(f"## {phase}")
            lines.append("")
            current_phase = phase

        lines.append(f"### Day {day:03d} — {topic}" if isinstance(day, int) else f"### Day {day} — {topic}")
        lines.append("")
        lines.append(f"- **Category:** {category}")
        lines.append(f"- **Difficulty:** {difficulty}")
        lines.append(f"- **Objective:** {objective}")
        lines.append("")

    ROADMAP_DOC_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    update_daily_index()
    update_roadmap_doc()
    print("Updated docs indexes.")


if __name__ == "__main__":
    main()