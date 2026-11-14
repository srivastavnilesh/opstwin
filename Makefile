.PHONY: bootstrap verify lint test clean

bootstrap:
	bash scripts/bootstrap.sh

verify:
	bash scripts/verify.sh

lint:
	.venv/bin/ruff check src tests config.py

test:
	.venv/bin/pytest -q

clean:
	rm -rf .pytest_cache .ruff_cache
	