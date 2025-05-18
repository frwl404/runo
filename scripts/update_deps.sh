#!/bin/sh

cd "$(dirname "$0")/../containers/$(printenv REGO_CONTAINER_NAME)/"

if command -v uv 2>&1 >/dev/null
then
    echo "updating deps with UV"
    uv lock --upgrade --no-cache
    exit 0
fi

if command -v pip 2>&1 >/dev/null
then
    echo "updating deps with PIP"
    pip-compile -U --cache-dir /tmp/.cache --strip-extras --output-file "pip.lock" "pip.in"
    exit 0
fi

echo "Oops, can't find how to update dependencies :("

