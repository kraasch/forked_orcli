
.PHONY: test
test:
	make clean
	#python -m pytest ./tests/src/test_refine_client_standalone.py
	#python -m pytest ./tests/src/test_refine_client_integration.py
	python -m pytest ./tests/ || true
	make clean

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +

