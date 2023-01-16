#!make
$(shell touch .env)
include .env

NAME := lcli
COVERAGE_PERCENTAGE := 0

SYSTEM_PYTHON = $(shell command -v python3 2> /dev/null)

RM = rm
PRJ_DIR = $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
VENV ?= $(PRJ_DIR)venv
POETRY ?= $(VENV)/bin/poetry
PYTHON ?= $(VENV)/bin/python
INSTALL_FLAG := $(VENV)/.install.$(NAME)

VERSION := $(VERSION_OVERWRITE)
VERSION := $(if $(VERSION),$(VERSION),$(shell $(POETRY) run python bin/print_version.py))

.DEFAULT_GOAL := help

.PHONY: help
help:
	@echo "Please use 'make <target>' where <target> is one of"
	@echo ""
	@echo "  install     install packages and prepare environment"
	@echo "  update      update packages all packages at the latest supported version"
	@echo "  clean       remove all temporary files"
	@echo "  lint        run the code linters"
	@echo "  format      reformat code"
	@echo "  test        run all the tests"
	@echo "  build       update the version, build the binaries, create the, git tag"
	@echo "  publish     publish the binaries"
	@echo ""
	@echo "Check the Makefile to know exactly what each target is doing."

$(VENV):
	@echo Create virtual environment in $(VENV)
	@if [ -z $(SYSTEM_PYTHON) ]; then echo "Python 3 could not be found."; exit 2; fi
	$(SYSTEM_PYTHON) -m venv $(VENV)

$(PYTHON): $(VENV)

$(POETRY):
	@echo Install poetry in $(VENV)
	$(PYTHON) -m pip install -r requirements/poetry.txt

.PHONY: install
install: $(INSTALL_FLAG)
$(INSTALL_FLAG): $(VENV) $(PYTHON) poetry.lock $(POETRY)
	@echo Poetry install all requirements in $(VENV)
	$(POETRY) install
	touch $(INSTALL_FLAG)

.PHONY: install_all
install_all: $(VENV) $(PYTHON) poetry.lock $(POETRY)
	@echo Poetry install all groups requirements in $(VENV)
	$(POETRY) install --with=test --with=docs --with=build --with=poetry --all-extras
	touch $(INSTALL_FLAG)

.PHONY: install_for_user
install_for_user:
	./install -u

.PHONY: install_for_system
install_for_system:
	./install

.PHONY: update
update: $(VENV) $(POETRY) pyproject.toml
	@echo Poetry install all requirements in $(VENV)
	$(POETRY) update

.PHONY: test
test: $(VENV) $(POETRY)
	@echo POETRY: test
	$(POETRY) run pytest --cov-report html --cov-report xml --cov-report term-missing --cov-fail-under $(COVERAGE_PERCENTAGE) --cov flex_cli --cov flex_framework

uninstall: $(VENV)
	$(VENV)/bin/pip uninstall -y $(NAME)

.PHONY: build
build: $(VENV) $(POETRY) install
	@echo POETRY: Build $(VERSION)
	$(POETRY) version $(VERSION)
	sed -i 's/__version__\(.*\)/__version__: str = "$(VERSION)"/' src/lcli/__init__.py
	$(POETRY) build

.PHONY: create_version
create_version: $(VENV) $(POETRY) install test lint build
	@echo POETRY: Create version $(VERSION)
	git add src/lcli/__init__.py pyproject.toml poetry.lock
	git commit -m "Bumping version to $(VERSION)" && true
	git push origin
	git tag $(VERSION)
	git push origin $(VERSION)
	@echo POETRY: Publish $(VERSION) on testpypi
	$(POETRY) publish --username="$(PYPI_TEST_USERNAME)" --password="$(PYPI_TEST_PASSWORD)" --repository="$(PYPI_TEST_REPOSITORY)"
	@echo POETRY: Create version done $(VERSION)

.PHONY: publish
publish: $(VENV) $(POETRY) install test lint build create_version
	@echo POETRY: publish $(VERSION)
	$(POETRY) publish --username="$(PYPI_USERNAME)" --password="$(PYPI_PASSWORD)" --repository="$(PYPI_REPOSITORY)"
	@echo POETRY: publish done $(VERSION)

upload_test: $(VENV)
	$(VENV)/bin/python3 -m twine upload --repository testpypi dist/* --verbose
	$(RM) -rf dist/*

upload: $(VENV)
	$(VENV)/bin/python3 -m twine upload dist/* --verbose
	$(RM) -rf dist/*

.PHONY: freeze
freeze: $(VENV) $(POETRY)
	@echo POETRY: export dependencies in txt files
	$(POETRY) export --without-hashes -f requirements.txt -o requirements/binary.txt
	$(POETRY) export --without-hashes -f requirements.txt -o requirements.txt
	$(POETRY) export --without-hashes --only dev > requirements/dev.txt
	$(POETRY) export --without-hashes --only docs > requirements/docs.txt
	$(POETRY) export --without-hashes --only build > requirements/build.txt
	$(POETRY) export --without-hashes --only test > requirements/test.txt
	$(POETRY) export --without-hashes --only poetry > requirements/poetry.txt

.PHONY: dependency
dependency:
	$(POETRY) -m poetry show --no-dev --tree

.PHONY: lint
lint: $(INSTALL_STAMP)
	@echo POETRY: Start lint check
	@echo POETRY: isort
	$(POETRY) run isort --profile=black --lines-after-imports=2 --check-only ./src --virtual-env=$(VENV)
	@echo POETRY: black
	$(POETRY) run black --check ./src --diff
	@echo POETRY: flake8
	$(POETRY) run flake8 --ignore=W503,E501,E203 ./src
	@echo POETRY: mypy
	$(POETRY) run mypy ./src/ --ignore-missing-imports
	@echo POETRY: bandit
	$(POETRY) run bandit -r ./src -c pyproject.toml
	@echo POETRY: Done the lint check

.PHONY: lint_fix
lint_fix: $(INSTALL_STAMP)
	@echo POETRY: Start lint fix
	@echo POETRY: isort
	$(POETRY) run isort --profile=black --lines-after-imports=2 ./src --virtual-env=$(VENV)
	@echo POETRY: black
	$(POETRY) run black ./src
	@echo POETRY: flake8
	$(POETRY) run flake8 --ignore=W503,E501,E203 ./src
	@echo POETRY: mypy
	$(POETRY) run mypy ./src --ignore-missing-imports
	@echo POETRY: bandit
	$(POETRY) run bandit -r ./src -c pyproject.toml
	@echo POETRY: Done the lint check

.PHONY: format
format: $(INSTALL_STAMP)
	$(VENV)/bin/isort --profile=black --lines-after-imports=2 ./tests/ $(NAME) --virtual-env=$(VENV)
	$(VENV)/bin/black ./tests/ $(NAME)

.PHONY: clean
clean:
	@echo Clean all
	$(POETRY) env remove --all
	$(PYTHON) -m pip uninstall -y poetry
	$(RM) -rf $(VENV) .coverage .mypy_cache build/* dist/* .pytest_cache htmlcov coverage.xml
	find . -type d -name "__pycache__" | xargs rm -rf {};
