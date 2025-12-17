PY_EXE:=python3
build:
	$(PY_EXE) -m venv .
	cat requirements.txt | xargs bin/pip install
install: build
	./bin/activate
	bin/pyinstaller --onefile teletal.py
	deactivate
dist/teletal: install
/usr/local/bin/teletal: dist/teletal
	sudo cp dist/teletal /usr/local/bin/teletal
	

bin/pylint:
	bin/pip install pylint
test: bin/pylint
	bin/pylint *.py
