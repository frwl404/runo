# At the moment of writing UV can't install python on top of alpine,
# So just take python image and install uv on top of it
FROM python:3.11-alpine

# UV, see https://docs.astral.sh/uv/guides/integration/docker/#available-images
COPY --from=ghcr.io/astral-sh/uv:0.6.4 /uv /uvx /bin/

WORKDIR /tmp/runo_venv
COPY containers/python311/pyproject.toml .
COPY containers/python311/uv.lock .

RUN uv sync
