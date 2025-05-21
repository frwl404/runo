#!/bin/sh

cd "$(dirname "$0")/../"

source /tmp/dev_venv/.venv/bin/activate

echo ">>> setting actual version ($(git describe --tags))"
sed -i "s/^__version__ = .*/__version__ = \"$(git describe --tags)\"/" ./dev

echo ">>> formatting the code with ruff"
ruff format ./dev tests

echo ">>> fixing the code with ruff"
ruff check ./dev tests --fix

echo ">>> mypy is checking the code"
mypy ./dev tests
