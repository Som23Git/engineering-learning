# Engineering Learning

This repo is my daily engineering learning system.

It uses:

- GitHub Actions for daily automation
- OpenAI API for lesson generation
- MkDocs Material for the learning website
- GitHub Pages for publishing
- A feedback loop from previous lessons to improve future lessons

## How it works

Every day:

1. GitHub Actions runs on a schedule.
2. The Python script reads `roadmap.json`.
3. It checks the previous day's feedback.
4. It asks OpenAI to generate today's lesson.
5. It saves the lesson under `docs/daily/`.
6. It updates docs index pages.
7. It commits the new lesson.
8. It deploys the MkDocs site to GitHub Pages.

## Human feedback loop

Each daily lesson includes:

- Learning Feedback
- Rating
- What was clear?
- What was confusing?
- What should be explained again?
- What should tomorrow include?

The next run reads this feedback and uses it to improve the next lesson.