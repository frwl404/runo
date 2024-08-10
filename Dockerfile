FROM python:3.9-alpine

RUN ln -s /usr/local/bin/python /usr/bin/python3 || echo "python is already on place"

WORKDIR /app

COPY rcmd rcmd
COPY tests tests
