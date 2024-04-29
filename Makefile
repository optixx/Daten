env-boostrap:
	rm -rvf .venv
	uv venv

pip-install:
	uv pip install -r requirements.txt

