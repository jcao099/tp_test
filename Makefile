.ONESHELL:


force_reload:

requirements:
	poetry export -f requirements.txt --output requirements.txt --without-hashes

format:
	poetry run autoflake -i -r transcripts --remove-all-unused-imports --ignore-init-module-imports
	poetry run isort transcripts -v
	poetry run black transcripts

check:
	poetry run isort transcripts -c -v
	poetry run black transcripts --check
	poetry run pyright
	poetry run flake8
	poetry run pylint transcripts
	poetry run bandit transcripts
	poetry run safety check

test: check
	poetry run pytest --cov=transcripts

test-only:
	poetry run pytest --cov=transcripts

sha:
	git rev-parse --short HEAD > checksum.txt

build:
	poetry build

docs: force_reload
	poetry run handsdown -n transcripts --theme=material --create-configs
	poetry run mkdocs build

docs-serve: docs
	poetry run mkdocs serve

docker-build-local:
	docker build \
		--network=host \
		-t transcripts:latest \
		.

docker-run-local: docker-build-local
	docker run --rm -ti \
		-p 8000:8000 \
		--env-file .envfile \
		transcripts:latest

demo:
	poetry run uvicorn transcripts.app:app