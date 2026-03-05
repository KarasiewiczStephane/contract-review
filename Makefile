.PHONY: install test lint lint-fix clean run streamlit docker

install:
	pip install -r requirements.txt
	python -m spacy download en_core_web_sm

test:
	pytest tests/ -v --tb=short --cov=src --cov-fail-under=80

lint:
	ruff check src/ tests/
	ruff format --check src/ tests/

lint-fix:
	ruff check --fix src/ tests/
	ruff format src/ tests/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

run:
	python -m src.main

streamlit:
	PYTHONPATH=. streamlit run src/dashboard/app.py

docker:
	docker build -t contract-review .
	docker run -p 8501:8501 contract-review
