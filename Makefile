all: pip-install run

env-boostrap:
	rm -rvf .venv
	uv venv

pip-install:
	uv pip install -r requirements.txt

run:
	python convert.py --path data --prefix 1kHz


clean:
	rm -f *.csv *.pdf
