---
name: update-readme
description: Synchronize README.md with the current AgroTECH repository
argument-hint: Describe the change you made, or leave blank to inspect the current repository
---

Update `README.md` so it accurately describes the current AgroTECH repository.

${input}

Inspect the repository before editing, especially `RUN_PROJECT.md`, `requirements.txt`, `backend/requirements.txt`, `pages/`, `css/`, `js/`, and `backend/`.

Check and update only information that is stale:

- features and role permissions
- routes and page listings
- startup commands and prerequisites
- dependencies and environment variables
- demo accounts and supported languages
- project structure

Preserve the current concise bilingual Markdown style. Do not invent details. Keep all paths relative to the repository root. At the end, report the README sections changed and any inconsistencies that require human confirmation.
