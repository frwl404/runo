FROM python:3.6-alpine

WORKDIR /tmp/rego_venv
COPY containers/python36/pip.in .
COPY containers/python36/pip.lock .

RUN apk add py3-virtualenv \
    && pip3 install pip-tools \
    && virtualenv -p python3.6 .venv \
    && source .venv/bin/activate \
    && pip3 install -r pip.lock
