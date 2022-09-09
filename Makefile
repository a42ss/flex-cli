PYTHON = python3
RM = rm

PRJ_DIR = $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
VENV ?= $(PRJ_DIR)venv

install: $(VENV) setup.py
	$(VENV)/bin/pip install -U .

install_reqs: $(VENV) setup.py
	$(VENV)/bin/pip install --system --deploy --ignore-pipfile

test: $(PYTHON)
	$(PYTHON) -m pytest

$(VENV):
	$(PYTHON) -m venv $(VENV)

uninstall: $(VENV)
	$(VENV)/bin/pip uninstall -y lcli

build: $(VENV)
	$(VENV)/bin/python3 -m build

upload_test: $(VENV)
	$(VENV)/bin/python3 -m twine upload --repository testpypi dist/* --verbose
	$(RM) -rf dist/*

upload: $(VENV)
	$(VENV)/bin/python3 -m twine upload dist/* --verbose
	$(RM) -rf dist/*

poetry_update:
	$(VENV)/bin/$(PYTHON) -m poetry update

# python -m pip freeze -r requirements_list.txt -l  | sed '/freeze/,$ d' > requirements.txt
# $(shell $(VENV)/bin/$(PYTHON) -m pip freeze -r requirements.txt -l | sed '/freeze/,$$ d' > requirements.txt)
poetry_freeze:
	$(shell $(VENV)/bin/$(PYTHON) -m poetry export --without-hashes -f requirements.txt -o requirements.txt)
	$(shell $(VENV)/bin/$(PYTHON) -m poetry export --without-hashes --only dev > requirements_dev.txt)
	$(shell $(VENV)/bin/$(PYTHON) -m poetry export --without-hashes --only docs > requirements_docs.txt)
	$(shell $(VENV)/bin/$(PYTHON) -m poetry export --without-hashes --only build > requirements_build.txt)
	$(shell $(VENV)/bin/$(PYTHON) -m poetry export --without-hashes --only test > requirements_test.txt)

poetry_dependency:
	$(VENV)/bin/$(PYTHON) -m poetry show --no-dev --tree

clean:
	$(RM) -rf $(VENV)
