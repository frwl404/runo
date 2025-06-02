# At the moment of writing UV can't install python on top of alpine,
# So just take python image and install uv on top of it
FROM python:3.8-alpine

# UV, see https://docs.astral.sh/uv/guides/integration/docker/#available-images
COPY --from=ghcr.io/astral-sh/uv:0.6.4 /uv /uvx /bin/

WORKDIR /tmp/rego_venv
COPY containers/python38/pyproject.toml .
COPY containers/python38/uv.lock .

RUN uv sync
