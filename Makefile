setup:
	python -m venv venv

install:
	pip install -r requirements.txt

run:
	python src/main.py

test:
	pytest

clean:
	rmdir /S /Q __pycache__