
.PHONY: test clean

run_clean_tests:
	make clean
	make test
	make clean

test:
	python -m venv .venv
	.venv/bin/python -m pip install --upgrade pip
	.venv/bin/python -m pip install -e ".[test]"
	.venv/bin/python -m pytest ./tests/
	#.venv/bin/python -m pytest ./tests/src/test_refine_client_standalone.py
	#.venv/bin/python -m pytest ./tests/src/test_refine_client_integration.py

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +

