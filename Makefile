all:
	python -m build


clean:
	rm -rf build/
	rm -rf dist/
	rm -rf TimeForge.egg-info/


upload: all
	twine upload dist/*

venv:
	bash ./setup-venv.sh
