#!/bin/sh
set -e
flake8 checksite tests
mypy --check-untyped-defs --ignore-missing-imports checksite tests
pytest --tb=short -q tests
