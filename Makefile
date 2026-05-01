.PHONY: run test install lint format clean

# Variáveis do projeto
PYTHON = python
VENV_DIR = venv

install:
	$(PYTHON) -m venv $(VENV_DIR)
	.\$(VENV_DIR)\Scripts\activate && pip install -r requirements.txt

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest -v

lint:
	flake8 app/ tests/

clean:
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf app/__pycache__
	rm -rf tests/__pycache__
