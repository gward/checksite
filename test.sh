#!/bin/sh
test -e
flake8 checksite
mypy --check-untyped-defs --ignore-missing-imports checksite
