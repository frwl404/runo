#!/bin/sh

cd "$(dirname "$0")/../"

source /tmp/runo_venv/.venv/bin/activate

echo ">>> setting actual version ($(git describe --tags))"
sed -i "s/^__version__ = .*/__version__ = \"$(git describe --tags)\"/" ./runo

echo ">>> formatting the code with ruff"
ruff format ./runo tests

echo ">>> fixing the code with ruff"
ruff check ./runo tests --fix

echo ">>> mypy is checking the code"
mypy ./runo tests
