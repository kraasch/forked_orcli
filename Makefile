
.PHONY: run-clean-tests test build test-wheel check publish clean

run-clean-tests:
	make clean
	make test
	make clean

test:
	python -m venv .venv
	.venv/bin/python -m pip install --upgrade pip
	.venv/bin/python -m pip install -e ".[test]"
	.venv/bin/python -m pytest ./tests/ -v
	#.venv/bin/python -m pytest ./tests/src/test_refine_client_standalone.py
	#.venv/bin/python -m pytest ./tests/src/test_refine_client_integration.py

build: test
	python -m venv .venv
	.venv/bin/python -m pip install --upgrade pip
	.venv/bin/python -m pip install build
	.venv/bin/python -m build

test-wheel: build
	python -m venv .venv-wheel
	.venv-wheel/bin/python -m pip install --upgrade pip
	.venv-wheel/bin/python -m pip install dist/*.whl
	.venv-wheel/bin/python -c "from orcli import Refine; print(Refine)"

check: test-wheel
	.venv/bin/python -m pip install twine
	.venv/bin/python -m twine check --strict dist/*

publish: check
	.venv/bin/python -m twine upload dist/*

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	rm -rf build dist *.egg-info src/*.egg-info
	find . -type d -name "temp_output" -exec rm -r {} +

