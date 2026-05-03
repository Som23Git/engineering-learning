import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from openai import OpenAI


ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "docs"
DAILY_DIR = DOCS_DIR / "daily"
ROADMAP_FILE = ROOT / "roadmap.json"

MODEL = os.getenv("OPENAI_MODEL", "gpt-5.5")


def slugify(text: str) -> str:
    value = text.lower().strip()
    value = value.replace("&", "and")
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value)
    return value.strip("-")


def load_roadmap() -> List[Dict[str, Any]]:
    if not ROADMAP_FILE.exists():
        raise FileNotFoundError("roadmap.json not found")

    with open(ROADMAP_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError("roadmap.json must be a JSON array")

    return data


def get_existing_daily_notes() -> List[Path]:
    DAILY_DIR.mkdir(parents=True, exist_ok=True)
    return sorted(
        [
            path
            for path in DAILY_DIR.glob("*.md")
            if path.name != "index.md"
        ]
    )


def get_day_number() -> int:
    return len(get_existing_daily_notes()) + 1


def extract_learning_feedback(markdown: str) -> str:
    """
    Extracts the feedback section from a previous lesson.

    Expected section:

    ## Learning Feedback

    ...content...

    ## Next Section
    """
    pattern = r"## Learning Feedback\s*(.*?)(?=\n## |\Z)"
    match = re.search(pattern, markdown, flags=re.DOTALL | re.IGNORECASE)

    if not match:
        return "No structured feedback was found in the previous lesson."

    feedback = match.group(1).strip()

    if not feedback:
        return "The previous lesson had a Learning Feedback section, but it was empty."

    return feedback


def read_previous_feedback() -> str:
    notes = get_existing_daily_notes()

    if not notes:
        return "This is the first lesson. There is no previous feedback yet."

    previous_note = notes[-1]

    with open(previous_note, "r", encoding="utf-8") as file:
        previous_content = file.read()

    feedback = extract_learning_feedback(previous_content)

    return f"""
Previous lesson file: {previous_note.name}

Previous learner feedback:

{feedback}
""".strip()


def markdown_links(items: List[Dict[str, str]]) -> str:
    if not items:
        return "- No links provided."

    lines = []

    for item in items:
        title = item.get("title", "Untitled")
        url = item.get("url", "")
        if url:
            lines.append(f"- [{title}]({url})")
        else:
            lines.append(f"- {title}")

    return "\n".join(lines)


def build_prompt(day_number: int, topic_item: Dict[str, Any], previous_feedback: str) -> str:
    topic = topic_item["topic"]
    phase = topic_item.get("phase", "Engineering Learning")
    category = topic_item.get("category", "Software Engineering")
    difficulty = topic_item.get("difficulty", "Beginner")
    learning_objective = topic_item.get("learning_objective", "")
    official_docs = markdown_links(topic_item.get("official_docs", []))
    good_reads = markdown_links(topic_item.get("good_reads", []))
    hands_on = topic_item.get("hands_on", "")
    expected_outcome = topic_item.get("expected_outcome", "")

    today = datetime.now(timezone.utc).date().isoformat()

    return f"""
You are my senior engineering mentor.

I am a junior engineer learning backend engineering, platform engineering,
distributed systems, cloud, DevOps, observability, reliability, and system design.

Generate a GitHub-ready Markdown lesson.

Important:
- Use the roadmap item as the source of truth.
- Use the official documentation links exactly as provided.
- Do not invent fake documentation links.
- Adapt today's explanation using the previous learner feedback.
- If the previous feedback mentioned confusion, briefly address that confusion when relevant.
- Keep the lesson practical and serious, not fluffy.
- Use simple language first, then technical depth.

Day: {day_number}
Date: {today}
Phase: {phase}
Topic: {topic}
Category: {category}
Difficulty: {difficulty}

Learning objective:
{learning_objective}

Official documentation links:
{official_docs}

Good reads:
{good_reads}

Hands-on task:
{hands_on}

Expected outcome:
{expected_outcome}

Previous feedback context:
{previous_feedback}

Generate the lesson using exactly this structure:

# Day {day_number:03d} — {topic}

Date: {today}

## Phase

Write the phase name.

## Learning Objective

Explain what I should understand by the end of this lesson.

## Why This Topic Matters

Explain why this matters in real backend/platform/production engineering.

## Simple Explanation

Explain it like I am new to engineering.

## Real-World Analogy

Give a practical analogy that is easy to remember.

## Technical Explanation

Go one level deeper technically.

## Practical Example

Include one practical example.
Use code, curl, architecture text, or config where useful.

## Official Documentation To Read

Include the official documentation links provided in the roadmap.

## Good Reads

Include the good-read links provided in the roadmap.

## Where This Appears in Production

Explain where this appears in real systems.

## Common Beginner Mistakes

List common misunderstandings and mistakes.

## Related Concepts

List related concepts I should connect this to.

## Interview-Level Explanation

Give a concise explanation I can use in interviews.

## Hands-On Exercise

Use the provided hands-on task and expand it into clear steps.

## Expected Outcome

Explain what I should be able to do after the exercise.

## Quiz Questions

Ask 3 questions to check my understanding.

## My Understanding

<!-- I will fill this manually after reading. -->

## Mistakes I Made

<!-- I will fill this manually after trying the exercise. -->

## Questions I Still Have

<!-- I will fill this manually. -->

## Learning Feedback

### Rating

<!-- 1 to 5 -->

### What was clear?

<!-- Fill after reading. -->

### What was confusing?

<!-- Fill after reading. -->

### What should be explained again?

<!-- Fill after reading. -->

### What style worked best?

<!-- Examples, analogy, diagrams, code, debugging story, etc. -->

### What should tomorrow include?

<!-- This will be read by the next automation run. -->

## What To Learn Next

Suggest the next logical topic based on the roadmap.
""".strip()


def generate_lesson(prompt: str) -> str:
    if "OPENAI_API_KEY" not in os.environ:
        raise EnvironmentError("OPENAI_API_KEY is not set")

    client = OpenAI()

    response = client.responses.create(
        model=MODEL,
        input=prompt,
    )

    return response.output_text.strip() + "\n"


def main() -> None:
    DAILY_DIR.mkdir(parents=True, exist_ok=True)

    roadmap = load_roadmap()
    day_number = get_day_number()

    if day_number > len(roadmap):
        raise ValueError(
            f"Roadmap completed. Day {day_number} requested, "
            f"but roadmap has only {len(roadmap)} items. "
            "Add more roadmap items before the next run."
        )

    topic_item = roadmap[day_number - 1]
    topic = topic_item["topic"]

    today = datetime.now(timezone.utc).date().isoformat()
    filename = f"{today}-day-{day_number:03d}-{slugify(topic)}.md"
    output_path = DAILY_DIR / filename

    if output_path.exists():
        print(f"File already exists: {output_path}")
        return

    previous_feedback = read_previous_feedback()
    prompt = build_prompt(day_number, topic_item, previous_feedback)
    lesson = generate_lesson(prompt)

    with open(output_path, "w", encoding="utf-8") as file:
        file.write(lesson)

    print(f"Created {output_path}")


if __name__ == "__main__":
    main()