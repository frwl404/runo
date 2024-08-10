#!/bin/sh

cd "$(dirname "$0")/../"

source /tmp/rego_venv/.venv/bin/activate

echo "formatting the code with ruff"
ruff format ./rego tests

echo "fixing the code with ruff"
ruff check ./rego tests --fix

echo "mypy is checking the code"
mypy ./rego tests