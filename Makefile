
.PHONY = help docs test

.DEFAULT_GOAL = help
PYTHON = python3
CURRENT_VERSION := $(shell ./scripts/version.sh)

help:
	echo "TODO"

lint:
	${PYTHON} -m pylint wropen

docs:
	pydoctor --make-html -c pyproject.toml --project-version=${CURRENT_VERSION}

wheel:
	${PYTHON} setup.py bdist_wheel
