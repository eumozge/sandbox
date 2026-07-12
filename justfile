py *args:
    uv run {{ if args == "" { "main.py" } else { args } }}

py-limits *args:
    ulimit -v 1048576 && just py {{args}}

install:
    uv sync --all-extras --all-groups

lint:
	just py ruff check --fix --unsafe-fixes && just py ruff format && uv run mypy app

test:
	just py pytest -s -v


main *args:
	just py python3 app {{args}}


storages-up:
    docker compose -f docker-compose.yaml --env-file .env -p dev up -d --remove-orphans

storages-down:
    docker compose -f docker-compose.yaml --env-file .env -p dev down

storages-clean:
    docker compose -f docker-compose.yaml --env-file .env -p dev down -v