import json
import os
from datetime import datetime, timezone
from pathlib import Path

from openai import OpenAI


ROOT = Path(__file__).resolve().parents[1]
DAILY_DIR = ROOT / "daily"
ROADMAP_FILE = ROOT / "roadmap.json"

MODEL = os.getenv("OPENAI_MODEL", "gpt-5.5")


def slugify(text: str) -> str:
    return (
        text.lower()
        .replace("&", "and")
        .replace("/", "-")
        .replace(" ", "-")
        .replace("_", "-")
    )


def get_day_number() -> int:
    existing_notes = sorted(DAILY_DIR.glob("*.md"))
    return len(existing_notes) + 1


def load_roadmap():
    if not ROADMAP_FILE.exists():
        raise FileNotFoundError("roadmap.json not found")

    with open(ROADMAP_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def build_prompt(day_number: int, topic: str, category: str) -> str:
    return f"""
You are my senior engineering mentor.

I am a junior engineer learning backend engineering, platform engineering,
distributed systems, cloud, DevOps, and system design.

Generate a GitHub-ready Markdown lesson.

Day: {day_number}
Topic: {topic}
Category: {category}

Use this structure:

# Day {day_number:03d} — {topic}

Date: {datetime.now(timezone.utc).date().isoformat()}

## Simple Explanation

## Why It Exists

## Real-World Analogy

## Technical Explanation

## Practical Example

## Where This Appears in Production

## Common Beginner Mistakes

## Related Concepts

## Interview-Level Explanation

## Hands-On Exercise

## Quiz Questions

## My Understanding

Leave this section blank for me to fill in.

## Mistakes I Made

Leave this section blank for me to fill in.

## Questions I Still Have

Leave this section blank for me to fill in.

## What To Learn Next

Teaching style:
- Beginner-friendly but technically serious.
- Avoid fluff.
- Explain acronyms.
- Use practical backend/platform engineering examples.
- Include one small code example or architecture example when useful.
- Keep it focused enough to read in 15–20 minutes.
- Do not make it sound like marketing content.
"""


def main():
    DAILY_DIR.mkdir(exist_ok=True)

    if "OPENAI_API_KEY" not in os.environ:
        raise EnvironmentError("OPENAI_API_KEY is not set")

    roadmap = load_roadmap()
    day_number = get_day_number()

    topic_item = roadmap[(day_number - 1) % len(roadmap)]
    topic = topic_item["topic"]
    category = topic_item.get("category", "Software Engineering")

    today = datetime.now(timezone.utc).date().isoformat()
    filename = f"{today}-day-{day_number:03d}-{slugify(topic)}.md"
    output_path = DAILY_DIR / filename

    if output_path.exists():
        print(f"File already exists: {output_path}")
        return

    client = OpenAI()

    prompt = build_prompt(day_number, topic, category)

    response = client.responses.create(
        model=MODEL,
        input=prompt,
    )

    content = response.output_text.strip() + "\n"

    with open(output_path, "w", encoding="utf-8") as file:
        file.write(content)

    print(f"Created {output_path}")


if __name__ == "__main__":
    main()