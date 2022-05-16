PYTHON = python3
RM = rm

PRJ_DIR = $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
VENV ?= $(PRJ_DIR)venv

install: $(VENV) setup.py
	$(VENV)/bin/pip install -U .

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

# python -m pip freeze -r requirements_list.txt -l  | sed '/freeze/,$ d' > requirements.txt
freeze:
	$(shell $(VENV)/bin/$(PYTHON) -m pip freeze -r requirements_list.txt -l | sed '/freeze/,$$ d' > requirements.txt)

clean:
	$(RM) -rf $(VENV)
