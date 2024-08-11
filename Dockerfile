FROM python:3.9-alpine

RUN ln -s /usr/local/bin/python /usr/bin/python3 || echo "python is already on place"
RUN apk update && apk add py3-virtualenv

WORKDIR /app
COPY rcmd_cfg/pip_requirements.lock /tmp/pip_requirements.lock
RUN virtualenv -p python3.9 /rcmd_venv \
    && . /rcmd_venv/bin/activate \
    && pip3 install pip-tools \
    && pip3 install -r /tmp/pip_requirements.lock
