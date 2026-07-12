# AGENTS.md

## Quick commands (use `just`)
- `just install` – setup environment (uv sync)
- `just test` – run all tests (pytest)
- `just lint` – ruff check --fix + ruff format + mypy
- `just py` – run main.py
- `just storages-up` / `just storages-down` – docker-compose services

## Project structure (non-obvious)
- Tests live only in `tests.py` (see `pytest.ini`)
- Config sources of truth: `.ruff.toml`, `mypy.ini`, `pytest.ini`
- Use `uv`, never mix with pip/venv/pdm

## Hard rules (from observed agent mistakes)
- **Fix the cause, not the symptom**
- **If you see changes you didn't make, leave them intact** – do not overwrite
- Never commit `.env` or `.venv`; update `.env.example` when adding vars
- Prefer adding new `just` recipes instead of long shell commands in this file

## Conventions (not obvious from linters)
- Imports: stdlib → third-party → local; blank lines between groups; absolute imports preferred
- Use `list[int]` over `List[int]` (modern generics)
- `Any` only when necessary – and document why
- Async tests: pytest-asyncio auto; no manual loop fixtures needed

## When to update this file
- **Add rule** only after same mistake repeats 2–3 times
- **Remove rule** when it becomes obsolete or obvious from code/config
- Keep this file short – ~50 lines max. If a rule needs long explanation, move to separate docs

## Sanity checklist (mental, not to copy-paste)
- Run `just lint` before finishing
- Keep diffs minimal – touch only files related to the task
- Re-check line length (100) – `ruff format` handles it
