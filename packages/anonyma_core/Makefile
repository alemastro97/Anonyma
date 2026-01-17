.PHONY: build test download-models clean-cache

build:
    docker-compose build

download-models:
    docker-compose run --rm anonyma-core python scripts/download_models.py

test:
    docker-compose run --rm anonyma-test

clean-cache:
    docker volume rm packages_flair-cache || true
    docker-compose down -v

rebuild: clean-cache build download-models

test-quick:
    docker-compose run --rm anonyma-core python examples/simple_test.py