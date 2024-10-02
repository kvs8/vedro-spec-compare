.PHONY: clean
clean:
	rm -r build dist vedro_spec_compare.egg-info .mypy_cache .pytest_cache

.PHONY: install
install:
	pip3 install --quiet -r requirements.txt -r requirements-dev.txt

.PHONY: install-package
install-package:
	python3 setup.py install

.PHONY: check
check: install-package clean

.PHONY: check-types
check-types:
	python3 -m mypy vedro_spec_compare --strict

.PHONY: check-imports
check-imports:
	python3 -m isort --check-only .

.PHONY: sort-imports
sort-imports:
	python3 -m isort .

.PHONY: check-style
check-style:
	python3 -m flake8 .

.PHONY: lint
lint: check-types check-style check-imports
