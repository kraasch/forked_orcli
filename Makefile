
.PHONY: test
test:
	make clean
	make test_new || true
	make clean

all:
	make clean
	pytest ./tests/ || true
	make clean

test_old:
	pytest ./tests/test_refine_client_basic.py

test_new:
	pytest ./tests/test_refine_client_new.py

clean:
	make clean_pycache

clean_pycache:
	find . -type d -name "__pycache__" -exec rm -r {} +

