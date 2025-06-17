PY_EXE:=python3
build:
	$(PY_EXE) -m venv .
	cat requirements.txt | xargs bin/pip install

bin/pylint:
	bin/pip install pylint
test: bin/pylint
	bin/pylint *.py
