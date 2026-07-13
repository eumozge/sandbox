py *args:
    uv run {{ if args == "" { "main.py" } else { args } }}

py-limits *args:
    ulimit -v 1048576 && just py {{args}}

install:
    uv sync --all-extras --all-groups

lint:
	just py ruff check --fix --unsafe-fixes && just py ruff format && just py mypy src

test:
	just py pytest -s -v

migrations-make message="":
    uv run alembic revision --autogenerate -m "{{message}}"

migrations-apply:
    uv run alembic upgrade head

main *args:
	just py python3 app {{args}}

storages-up:
    docker compose -f dockercompose/dev.storages.yaml --env-file .env -p dev up -d --remove-orphans

storages-down:
    docker compose -f dockercompose/dev.storages.yaml --env-file .env -p dev down

storages-clean:
    docker compose -f dockercompose/dev.storages.yaml --env-file .env -p dev down -v