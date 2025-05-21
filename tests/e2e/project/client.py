#!/usr/local/bin/python3
import os
import subprocess
import sys


def do_curl() -> int:
    return subprocess.run(
        ["curl", "-s", "-I", "http://server:8000"], stdout=open(os.devnull, "wb")
    ).returncode


def do_ping() -> int:
    return subprocess.run(["ping", "-c", "1", "server"], stdout=open(os.devnull, "wb")).returncode


if __name__ == "__main__":
    rc = 0
    if do_curl() != 0:
        rc = 1
        print("Curl NOK")
    if do_ping() != 0:
        rc = 1
        print("Ping NOK")

    if rc == 0:
        print("All tests passed")

    sys.exit(rc)

# docker compose -f dev/docker-compose.yml run --build client ./client.py
# docker compose -f dev/docker-compose.yml run --build --volume
# /home/anton/repos/dev/examples/docker_compose/:/anton client /anton/dev/client.py
