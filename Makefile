# Makefile for django_coverage_plugin

default:
	@echo "* No default action *"

clean:
	-rm -rf *.egg-info
	-rm -rf build dist
	-rm -f *.pyc */*.pyc */*/*.pyc */*/*/*.pyc */*/*/*/*.pyc */*/*/*/*/*.pyc
	-rm -f *.pyo */*.pyo */*/*.pyo */*/*/*.pyo */*/*/*/*.pyo */*/*/*/*/*.pyo
	-rm -f *.bak */*.bak */*/*.bak */*/*/*.bak */*/*/*/*.bak */*/*/*/*/*.bak
	-rm -rf __pycache__ */__pycache__ */*/__pycache__ */*/*/__pycache__ */*/*/*/__pycache__ */*/*/*/*/__pycache__
	-rm -f MANIFEST
	-rm -f .coverage .coverage.* coverage.xml
	-rm -f setuptools-*.egg distribute-*.egg distribute-*.tar.gz

sterile: clean
	-rm -rf .tox*

SDIST_CMD = python setup.py sdist --formats=gztar

kit:
	$(SDIST_CMD)

kit_upload:
	$(SDIST_CMD) upload

pypi:
	python setup.py register
