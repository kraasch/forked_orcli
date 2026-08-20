
.PHONY: test
test:
	make clean
	#python -m pytest ./tests/ || true
	python -m pytest ./tests/test_refine_client_basic.py
	#python -m pytest ./tests/test_refine_client_new.py
	make clean

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +

