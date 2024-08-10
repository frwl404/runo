import os
import pathlib
from contextlib import contextmanager

import pytest
import toml
from rego import TomlParser


@contextmanager
def _config_file(content: str, config_path: pathlib.Path):
    with open(config_path, "w") as f:
        f.write(content)

    res = open(config_path, "rb")
    try:
        yield res
    finally:
        res.close()
        os.remove(config_path)


@pytest.mark.parametrize(
    "content",
    [
        # Regular case
        {
            "docker_containers": [
                {
                    "name": "image_based_on_docker_file",
                    "docker_file_path": "/tmp/Dockerfile",
                },
                {
                    "name": "image_from_repo",
                    "docker_image": "python:3.9-alpine",
                    "docker_build_options": "-it",
                },
            ]
        },
        # Parameter value is a list
        {
            "commands": [
                {
                    "value_as_list": ["test --pdb"],
                }
            ]
        },
        # Root-level settings (not sections)
        {
            "commands": "hello",
        },
    ],
)
def test_ok(tmp_path, content):
    with _config_file(
        toml.dumps(content),
        config_path=tmp_path / "cfg.toml",
    ) as f:
        assert TomlParser().load(f) == content
