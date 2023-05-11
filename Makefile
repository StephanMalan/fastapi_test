run_dev:
	docker compose up --force-recreate --remove-orphans --build

run_test:
	docker compose -f docker-compose.dev.yml up --build

lint:
	ruff ./ && pylint ./src && mypy . --explicit-package-bases
	