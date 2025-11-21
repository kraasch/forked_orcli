
.PHONY: test
test:
	make clean
	pytest ./tests/

clean:
	make clean_pycache

clean_pycache:
	find . -type d -name "__pycache__" -exec rm -r {} +

