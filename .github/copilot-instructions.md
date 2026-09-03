# AgroTECH README maintenance

When changing the project, keep `README.md` accurate when the change affects:

- user roles, permissions, routes, or pages
- frontend or backend startup commands
- API behavior, dependencies, environment variables, or database setup
- demo accounts, supported languages, or project structure

Use the actual files in the repository as the source of truth. Check `RUN_PROJECT.md`, `requirements.txt`, `backend/requirements.txt`, `pages/`, `css/`, `js/`, and `backend/` before editing README content.

README update rules:

- Preserve the existing bilingual AgroTECH product description and concise Markdown style.
- Do not claim features, accounts, commands, or files that do not exist.
- Keep paths relative to the repository root.
- Keep startup instructions consistent with `RUN_PROJECT.md`.
- Update the project tree when files are added, removed, or renamed.
- Do not rewrite unrelated sections or add generated noise.
- After code changes, review the README diff for stale paths and broken commands.
