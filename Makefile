build:
	python -m build


clean:
	rm -rf build/
	rm -rf dist/
	rm -rf TimeForge.egg-info/


upload: build
	twine upload dist/*

venv:
	bash ./setup-venv.sh
