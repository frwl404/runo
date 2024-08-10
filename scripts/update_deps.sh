#!/bin/sh

cd "$(dirname "$0")/../containers/$(printenv REGO_CONTAINER_NAME)/"

uv lock --upgrade
