all: info clean flake8 test upload release
.PHONY: all docs upload info req

PACKAGE_NAME := $(shell python setup.py --name)
PACKAGE_VERSION := $(shell python setup.py --version)
PYTHON_PATH := $(shell which python)
PLATFORM := $(shell uname -s | awk '{print tolower($0)}')
DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
PYTHON_VERSION := $(shell python2 -c "import sys; print('py%s%s' % sys.version_info[0:2] + ('-conda' if 'conda' in sys.version or 'Continuum' in sys.version else ''))")
PYENV_HOME := $(DIR)/.tox/$(PYTHON_VERSION)-$(PLATFORM)/
ifneq (,$(findstring conda,$(PYTHON_VERSION)))
CONDA:=1
endif

ifndef GIT_BRANCH
GIT_BRANCH=$(shell git branch | sed -n '/\* /s///p')
endif

info:
	@echo "INFO:	Building $(PACKAGE_NAME):$(PACKAGE_VERSION) on $(GIT_BRANCH) branch"
	@echo "INFO:	Python $(PYTHON_VERSION) from $(PYENV_HOME) [$(CONDA)]"

clean:
	@find . -name "*.pyc" -delete
	@rm -rf .tox/*-$(PLATFORM) .tox/docs dist/* .tox/dist .tox/log docs/build/*

package:
	python setup.py sdist bdist_wheel

install: prepare
	$(PYENV_HOME)/bin/pip install .

uninstall:
	$(PYENV_HOME)/bin/pip uninstall -y $(PACKAGE_NAME)

venv: $(PYENV_HOME)/bin/activate

# virtual environment depends on requriements files
$(PYENV_HOME)/bin/activate: requirements*.txt
	@echo "INFO:	(Re)creating virtual environment..."
ifdef CONDA
	test -e $(PYENV_HOME)/bin/activate || conda create -y --prefix $(PYENV_HOME) pip
else
	test -e $(PYENV_HOME)/bin/activate || virtualenv --python=$(PYTHON_PATH) --system-site-packages $(PYENV_HOME)
endif
	$(PYENV_HOME)/bin/pip install -q -r requirements.txt -r requirements-test.txt
	touch $(PYENV_HOME)/bin/activate

prepare: venv
	pyenv install -s 2.7.13
	pyenv local 2.7.13
	@echo "INFO:	=== Prearing to run for package:$(PACKAGE_NAME) platform:$(PLATFORM) py:$(PYTHON_VERSION) dir:$(DIR) ==="

flake8: venv
	@echo "INFO:	flake8"
	$(PYENV_HOME)/bin/python -m flake8
	$(PYENV_HOME)/bin/python -m flake8 --install-hook 2>/dev/null || true

test: prepare flake8
	@echo "INFO:	test"
	$(PYENV_HOME)/bin/python setup.py build test sdist bdist_wheel check --restructuredtext --strict

test-cli:
	$(PYENV_HOME)/bin/python -c "import octario; print(octario.__version__)"

test-all:
	@echo "INFO:	test-all (extended/matrix tests)"
	# tox should not run inside virtualenv because it does create and use multiple virtualenvs
	pip install -q tox tox-pyenv
	python -m tox --skip-missing-interpreters true

upload:
ifeq ($(GIT_BRANCH),develop)
	@echo "INFO:	Upload package to testpypi.python.org"
	$(PYENV_HOME)/bin/python setup.py check --restructuredtext --strict
	$(PYENV_HOME)/bin/python setup.py sdist bdist_wheel upload -r https://testpypi.python.org/pypi
endif
ifeq ($(GIT_BRANCH),master)
	@echo "INFO:	Upload package to pypi.python.org"
	$(PYENV_HOME)/bin/python setup.py check --restructuredtext --strict
	$(PYENV_HOME)/bin/python setup.py sdist bdist_wheel upload
endif
