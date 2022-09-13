# Introduction

[![PyPI version](https://img.shields.io/pypi/v/flex-cli.svg)](https://pypi.org/project/flex-cli)
[![Build Status](https://github.com/a42ss/flex-cli/actions/workflows/python-package.yml/badge.svg)](https://github.com/a42ss/flex-cli/actions/workflows/python-package.yml)
[![Coverage badge](https://raw.githubusercontent.com/a42ss/flex-cli/python-coverage-comment-action-data/badge.svg)](https://github.com/a42ss/flex-cli/tree/python-coverage-comment-action-data)
[![CodeQL](https://github.com/a42ss/flex-cli/actions/workflows/codeql-analysis.yml/badge.svg?branch=main)](https://github.com/a42ss/flex-cli/actions/workflows/codeql-analysis.yml)
[![CII Best Practices](https://bestpractices.coreinfrastructure.org/projects/6480/badge)](https://bestpractices.coreinfrastructure.org/projects/6480)
[![Docs badge](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://flex-cli.readthedocs.io/en/latest)
[![Chat badge](https://img.shields.io/badge/chat-IRC-brightgreen.svg)](https://github.com/a42ss/flex-cli/discussions)
[![License](https://img.shields.io/badge/license-MIT-brightgreen.svg)](https://flex-cli.readthedocs.io/en/latest)

   

Local development productivity tools meant to smooth and ease developers day to day work. 
It is meant to be cross-platform but for now is tested using MacOs and Ubuntu

## This are few examples

* unified command line interfaces for multiple cli tools
* interactive command line mode

  - this act as an interactive wrapper on top of existing cli tools
  - also allow extending the existing cli tools with auto-completion, input enhanced wizard or description
  - allow switching between command namespaces in the same terminal

* Implement custom CLI tools using Python, fully integrate with all LCLI tool features:
  - just write some code class or function and configure them to be wired in application

* use Fire to auto document Python objects, so all you should do is to focus on business logic
   
# Features

## Fire mode

In fire mode the application allow user to configure a hierarchy of objects that fit its needs for various project.
The user can navigate and execute the hierarchy using Fire library by Google. 
"Python Fire is a library for automatically generating command line interfaces (CLIs) from absolutely any Python object."
https://github.com/google/python-fire

## Interactive mode

Most often during the development process developers are using various tools for various projects.
The interactive mode purpose is to improve productivity by offering auto-completion details on the spot.
This is implemented on top of python cmd package: https://docs.python.org/3/library/cmd.html

# Getting Started

## Installation process

Install from source

```bash
# Using invoke
invoke install
#from project root directory
./install
#or 
python3 -m pip install -r requirements.txt
python3 -m pip install . --user
```

## Software dependencies

This is a Python package available as MIT License and is depending on following packages:
 
* fire https://github.com/google/python-fire/releases
* pinject https://github.com/google/pinject/releases
* PyYAML
* prompt_toolkit
* pyfiglet
* blessings
* tk
* appJar
* jsonschema

## Latest releases

- V-0.2.2 - First released version. 

## API references

# Build and Test

## Build

```bash
# Using invoke
invoke build
```

## Test

```bash
# Using invoke
invoke test
invoke coverage
# Using pytest
py.test
pytest --cov=src/lcli/ .
```

# Use cases

[<img src="https://img.youtube.com/vi/L9orYXE1nlU/hqdefault.jpg" width="50%">](https://youtu.be/L9orYXE1nlU)

# Usage


## Configuration

# Author

[George Babarus](https://github.com/georgebabarus)

# Contribute

Feel free to contribute to this project and make developer life essayer:
- by submitting new ideas as a github issue [here](https://github.com/georgebabarus/lcli/issues/new)
- by making pull request with specific bug fixes
- for new features or architectural change please contact [George Babarus](https://github.com/georgebabarus) to avoid double work on any way.

# Useful links

* https://mypy.readthedocs.io/en/latest/generics.html#generics
* https://code-maven.com/interactive-shell-with-cmd-in-python
* https://www.journaldev.com/16140/python-system-command-os-subprocess-call
* https://stackoverflow.com/questions/3262569/validating-a-yaml-document-in-python
* https://github.com/oclif/oclif#-cli-types
* https://medium.com/the-z/getting-started-with-oclif-by-creating-a-todo-cli-app-b3a2649adbcf
* https://opensource.com/article/17/5/4-practical-python-libraries

