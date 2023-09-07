SHELL := /bin/bash

.SILENT: clean
.IGNORE: clean

build:	clean
	python -m build
	twine check --strict dist/*

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf src/TimeForge.egg-info/
	rm -rf venv/test
	rm -rf `find . -type d -name __pycache__`

devenv:	
	python -m venv venv/
	. venv/bin/activate; pip install -e .
	. venv/bin/activate; pip install ptpython
	. venv/bin/activate; pip install pynvim

