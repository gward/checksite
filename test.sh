#!/bin/sh
set -e
flake8 --ignore=E731 checksite tests
mypy --check-untyped-defs --ignore-missing-imports checksite tests
pytest --tb=short -q tests
