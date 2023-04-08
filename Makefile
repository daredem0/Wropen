
.PHONY = help docs test

.DEFAULT_GOAL = help
PYTHON = python3
CURRENT_VERSION := $(shell ./scripts/version.sh)

help:
	echo "TODO"

lint:
	[ -d "pylint" ] && rm -rf pylint || echo ""
	${PYTHON} scripts/codequality.py -l -m wropen -t 9.0
# && [ [ $? != "1" ] && [ $? != "2" ] ] exit 0
docs:
	pydoctor --make-html -c pyproject.toml --project-version=${CURRENT_VERSION}

wheel:
	${PYTHON} setup.py bdist_wheel

clean:
	rm -rf doc pylint *.egg-info build dist .mypy*
	find . -name __pycache__ -type d -exec rm {}/* \;
	find . -name __pycache__ -type d -exec rmdir {} \;
