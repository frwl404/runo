import os
import pathlib
import subprocess
import sys
from contextlib import contextmanager
from typing import List
from unittest.mock import call, patch

import pytest
import toml
from rego import main  # noqa

_OK_EXIT_CODE_REGEX = f"^{os.EX_OK}$"


@contextmanager
def _config_file(content: str, config_path: pathlib.Path):
    with open(config_path, "w") as toml_file:
        toml_file.write(content)
    try:
        yield config_path
    finally:
        os.remove(config_path)


class TestArguments:
    @pytest.mark.parametrize("help_flag", ["-h", "--help"])
    def test_help_message(self, capfd, monkeypatch, help_flag):
        monkeypatch.setattr(sys, "argv", ["rego", help_flag])

        with pytest.raises(SystemExit, match=_OK_EXIT_CODE_REGEX):
            main()

        std_out, std_err = capfd.readouterr()
        assert std_err == ""
        expected_strings = [
            "usage: rego [-c CONTAINER] [-d] [--config CONFIG] [--containers] [--init] [-h]",
            "            ...",
            "",
            "positional arguments:",
            "  command               exact command to be executed (might be supplemented",
            "                        with options). You could try `./rego.py` to get list",
            "                        of available commands.",
            "",
            "option",  # can be "optional arguments:" in old versions and "options:" on new
            "-c CONTAINER, --container CONTAINER",
            "                        force command to be run in specific container(s). Use",
            '                        "*" to run in all containers',
            "  -d, --debug           verbose output",
            "  --config CONFIG       path to the actual config file",
            "  --init                create and initialize config file",
            "  --containers          show all containers, present in the config file",
            "  -h, --help",
            "",
        ]

        assert len(std_out.split("\n")) == len(expected_strings)
        for expected_string in expected_strings:
            assert expected_string in std_out

    @pytest.mark.parametrize(
        "config_content, expected_output",
        [
            (
                {},
                "No any valid container configuration found\n",
            ),
            (
                {"containers": []},
                "No any valid container configuration found\n",
            ),
            (
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
                """Following containers are available:
  * image_based_on_docker_file
  * image_from_repo
""",
            ),
        ],
    )
    def test_containers(self, capfd, monkeypatch, config_content, expected_output):
        monkeypatch.setattr(sys, "argv", ["rego", "--containers"])
        config_path = pathlib.Path(os.getcwd()) / "rego.py.toml"

        with pytest.raises(SystemExit, match=_OK_EXIT_CODE_REGEX), _config_file(
            toml.dumps(config_content),
            config_path,
        ):
            main()

        std_out, std_err = capfd.readouterr()
        assert std_err == ""
        assert std_out == expected_output

    @pytest.mark.parametrize("config_flag", ["--config"])
    def test_config_flag(self, capfd, monkeypatch, config_flag, tmp_path):
        config_path = tmp_path / "cfg.toml"
        monkeypatch.setattr(sys, "argv", ["rego", config_flag, str(config_path)])

        config_content = toml.dumps(
            {
                "commands": [
                    {
                        "name": "test",
                        "description": "run tests",
                        "execute": "echo PASSED",
                        "examples": ["test --pdb"],
                    },
                    {
                        "name": "build",
                        "description": "build the project",
                        "execute": "echo DONE",
                    },
                ]
            }
        )
        with pytest.raises(SystemExit, match=_OK_EXIT_CODE_REGEX), _config_file(
            config_content, config_path
        ):
            main()

        std_out, std_err = capfd.readouterr()
        assert std_err == ""
        assert (
            std_out
            == """Following commands are available:
  * test - run tests ['./rego.py test --pdb']
  * build - build the project ['./rego.py build']
"""
        )

    @pytest.mark.parametrize("debug_flag", ["-d", "--debug"])
    def test_debug_flag(self, capfd, monkeypatch, debug_flag):
        monkeypatch.setattr(sys, "argv", ["rego", debug_flag])

        with pytest.raises(SystemExit, match=_OK_EXIT_CODE_REGEX):
            main()

        std_out, std_err = capfd.readouterr()
        assert std_err == ""
        assert (
            std_out
            == """[DEBUG] debug logging enabled
Config is not created yet.
Please initialize it with './rego.py --init'
"""
        )

    def test_unexpected_option(self, capfd, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["rego", "--wrong-option"])

        with pytest.raises(SystemExit, match="^2$"):
            main()

        std_out, std_err = capfd.readouterr()
        assert std_out == ""
        assert (
            std_err
            == """usage: rego [-c CONTAINER] [-d] [--config CONFIG] [--containers] [--init] [-h]
            ...
rego: error: unrecognized arguments: --wrong-option
"""
        )


class TestInit:
    """
    '--init' is quite special option, which deserve its own test class
    """

    INIT_CONTENT = """
# This is auto-generated file, which contains recommended set of commands and examples.
# To make it working for you project, please update configuration.
# For real-word examples, please check https://github.com/frwl404/rego
# You can find all details, needed for updating it to your needs in:
# https://github.com/frwl404/rego/blob/main/docs/CONFIG

#######################################################
# Examples of commands
#######################################################
[[commands]]
name = "test"
description = "runs unit tests"
# OPTIONALLY, you can specify actions, which you want to perform before the main command.
# For python projects, you may want to activate venv here.
before = ["echo This is just an exampe", "echo You should configure your tests here"]
# Actual command to run (can be single command, or script).
# You can pass additional options to this executable via console (see 'examples' section)
execute = "echo ALL TESTS PASSED"
# OPTIONALLY, you can specify actions, which you want to perfrom after the main command
# to do cleanup
after =["echo done > /dev/null"]
# OPTIONALLY, you can specify examples of command usage.
# if missing, ./rego will auto generate single example.
examples = ["tests --cov -vv", "tests --last-failed"]
## OPTIONALLY you can specify container, in which command should be executed by defaut.
## Container must be defined in the same file.
## It can be overwritten, or set from CLI as well.
# docker_container = "alpine"
## OPTIONALLY, you can specify 'docker run' options, which should be used at command execution.
## See official docker documentation: https://docs.docker.com/reference/cli/docker/container/run/
# docker_run_options = "-it -v .:/app -w /app"

[[commands]]
name = "build"
description = "builds the project"
execute = "echo Buld is running"
after = ["echo done"]
#docker_container = "alpine"
#docker_run_options = "-it -v .:/app -w /app"

[[commands]]
name = "shell"
description = "debug container by running shell in interactive mode (keep container running)"
execute = "/bin/sh"
docker_container = "alpine"
docker_run_options = "-it -v .:/app -w /app"

[[commands]]
name = "pre-commit"
description = "quick checks/fixes of code formatting (ruff/mypy)"
execute = "echo Ruff is formatting the code"
after = ["echo Formating completed"]
#execute = "scripts/pre_commit.sh"
#docker_container = "alpine"
#docker_run_options = "-v .:/app -w /app"

[[commands]]
name = "update-deps"
description = "updates dependencies, used in project, to the latest versions"
execute = "echo Often it is pain, but if you will script it and put here, it will be super easy"
#execute = "scripts/update-requirements.sh"
#docker_container = "alpine"
#docker_run_options = "-v .:/app -w /app"

#######################################################
# Examples of containers
#######################################################

# 1.1) Single container, based on image from repo.
# This is the simplest case, you should just specify target image:
[[docker_containers]]
name = "alpine"
docker_image = "alpine:3.14"

## 1.2) Single container, based on your local Docker file:
#[[docker_containers]]
#name = "python39"
## docker_file_path may be relative to './rego' file (recommended way),
## or absolute, what is also supported, but this is not what you usually need.
#docker_file_path = "containers/python39/Dockerfile"
## OPTIONALLY, you can provide build options, which you want
## to be used for building of your image, see:
## https://docs.docker.com/reference/cli/docker/buildx/build/
#docker_build_options = "--tag img-defined-by-docker-file"
#
## 2) Composition of multiple containers, based on your docker-compose.yml file
## This is probably most common (and also most complicated case)
#[[docker_containers]]
#name = "app-with-db"
## Compose file path may be relative to './rego' file (recommended way),
## or absolute, what is also supported, but this is not what you usually need.
#docker_compose_file_path = "docker-compose.yml"
## You should specify those service in compose file, whose container should
## be used to run commands in
#docker_compose_service = "app"
## OPTIONALLY you can specify options, which should be passed to docker-compose
## to run your command. For details see official docker documentation:
## https://docs.docker.com/reference/cli/docker/compose/
#docker_compose_options = "--all-resources"
"""

    def _assert_file_content(self, path: pathlib.Path, expected_content: str):
        assert path.is_file()
        assert path.read_text() == expected_content

    def test_fresh_setup(self, capfd, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["rego", "--init"])
        default_config_path = pathlib.Path("rego.py.toml")
        assert default_config_path.is_file() is False

        with pytest.raises(SystemExit, match=_OK_EXIT_CODE_REGEX):
            main()

        self._assert_file_content(default_config_path, self.INIT_CONTENT)
        default_config_path.unlink()

        std_out, std_err = capfd.readouterr()
        assert std_err == ""
        assert std_out == f"config created: {default_config_path}\n"

    def test_already_exist(self, capfd, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["rego", "--init"])
        default_config_path = pathlib.Path("rego.py.toml")
        open(default_config_path, "a").close()

        with pytest.raises(SystemExit, match=f"^{os.EX_PROTOCOL}$"):
            main()

        self._assert_file_content(default_config_path, "")
        default_config_path.unlink()

        std_out, std_err = capfd.readouterr()
        assert (
            std_err
            == """file 'rego.py.toml' already exist.
Please review that file. If it is needed, you can either:
- keep it on the same place, and generate new config under different path/name (use '--config')
- move it to other place and try to call '--init' again
If you don't need that file, just remove it and try again.
"""
        )
        assert std_out == ""

    def test_init_under_non_default_path(self, capfd, monkeypatch):
        non_default_config_path = pathlib.Path("test_config.toml")
        monkeypatch.setattr(
            sys, "argv", ["rego", "--init", "--config", str(non_default_config_path)]
        )
        default_config_path = pathlib.Path("rego.py.toml")
        open(default_config_path, "a").close()

        with pytest.raises(SystemExit, match=_OK_EXIT_CODE_REGEX):
            main()

        self._assert_file_content(default_config_path, "")
        self._assert_file_content(non_default_config_path, self.INIT_CONTENT)
        default_config_path.unlink()
        non_default_config_path.unlink()

        std_out, std_err = capfd.readouterr()
        assert std_err == ""
        assert std_out == f"config created: {non_default_config_path}\n"


class TestMainOutput:
    def test_without_config_file(self, capfd, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["rego"])

        with pytest.raises(SystemExit, match=_OK_EXIT_CODE_REGEX):
            main()

        std_out, std_err = capfd.readouterr()
        assert std_err == ""
        assert (
            std_out
            == """Config is not created yet.
Please initialize it with './rego.py --init'
"""
        )

    def test_config_file(self, capfd, monkeypatch):
        config_path = pathlib.Path(os.getcwd()) / "rego.py.toml"
        monkeypatch.setattr(sys, "argv", ["rego"])

        with pytest.raises(SystemExit, match=_OK_EXIT_CODE_REGEX), _config_file(
            toml.dumps(
                {
                    "commands": [
                        {
                            "name": "test",
                            "execute": "pytest",
                            "description": "good command",
                            "examples": ["pytest --pdb"],
                        },
                        {
                            "name": "will_not_work_without_description",
                            "execute": "pytest",
                        },
                    ]
                }
            ),
            config_path,
        ):
            main()

        std_out, std_err = capfd.readouterr()
        assert (
            std_err
            == """errors detected in configured commands:
  - commands.1.description: ['mandatory field missing']
"""
        )
        assert (
            std_out
            == """Following commands are available:
  * test - good command ['./rego.py pytest --pdb']
"""
        )

    def test_wrong_path_to_config_file(self, capfd, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["rego", "--config", "/tmp/missing.toml"])

        with pytest.raises(SystemExit, match=f"^{os.EX_UNAVAILABLE}$"):
            main()

        std_out, std_err = capfd.readouterr()
        assert std_err == (
            "file, which you tried to use as config, doesn't exist: '/tmp/missing.toml'\n"
        )
        assert std_out == ""


class TestConfigCommandsFormat:
    @pytest.mark.parametrize(
        "config_content, expected_rc, expected_err_out, expected_std_out",
        [
            (
                {},
                os.EX_OK,
                "",
                "Config file is present, but there are no any valid commands configured there\n",
            ),
            (
                {"commands": []},
                os.EX_OK,
                "",
                "Config file is present, but there are no any valid commands configured there\n",
            ),
            (
                {"commands": {}},
                os.EX_CONFIG,
                """errors detected in configured commands:
  - commands should be represented by list, got dict
""",
                "Config file is present, but there are no any valid commands configured there\n",
            ),
            (
                {"commands": "hello"},
                os.EX_CONFIG,
                """errors detected in configured commands:
  - commands should be represented by list, got str
""",
                "Config file is present, but there are no any valid commands configured there\n",
            ),
            (
                {"commands": ["hello"]},
                os.EX_CONFIG,
                """errors detected in configured commands:
  - commands.0.*: ["must be represented by 'dict', got 'str'"]
""",
                "Config file is present, but there are no any valid commands configured there\n",
            ),
            (
                {"commands": [{}]},
                os.EX_CONFIG,
                """errors detected in configured commands:
  - commands.0.description: ['mandatory field missing']
  - commands.0.execute: ['mandatory field missing']
  - commands.0.name: ['mandatory field missing']
""",
                "Config file is present, but there are no any valid commands configured there\n",
            ),
            (
                {"commands": [{"name": 13, "wrong_field": "something"}]},
                os.EX_CONFIG,
                """errors detected in configured commands:
  - commands.0.description: ['mandatory field missing']
  - commands.0.execute: ['mandatory field missing']
  - commands.0.name: ['should be of type str, got int']
  - commands.0.wrong_field: ['unsupported field']
""",
                "Config file is present, but there are no any valid commands configured there\n",
            ),
            (  # Test 'name' field format
                {
                    "commands": [
                        {
                            "name": "spaces are not allowed",
                            "execute": "echo",
                            "description": "anything",
                        },
                        {
                            "name": "slashes/are/not/allowed",
                            "execute": "echo",
                            "description": "anything",
                        },
                        {
                            "name": "#not_allowed_also",
                            "execute": "echo",
                            "description": "anything",
                        },
                        {
                            "name": "?not_allowed_also",
                            "execute": "echo",
                            "description": "anything",
                        },
                    ]
                },
                os.EX_CONFIG,
                """errors detected in configured commands:
  - commands.0.name: ["should consist only of letters, \
digits, '-', or '_', got 'spaces are not allowed'"]
  - commands.1.name: ["should consist only of letters, \
digits, '-', or '_', got 'slashes/are/not/allowed'"]
  - commands.2.name: ["should consist only of letters, \
digits, '-', or '_', got '#not_allowed_also'"]
  - commands.3.name: ["should consist only of letters, \
digits, '-', or '_', got '?not_allowed_also'"]
""",
                "Config file is present, but there are no any valid commands configured there\n",
            ),
        ],
    )
    def test_nok_commands(
        self,
        capfd,
        monkeypatch,
        tmp_path,
        config_content,
        expected_rc,
        expected_err_out,
        expected_std_out,
    ):
        config_path = tmp_path / "cfg.toml"
        monkeypatch.setattr(sys, "argv", ["rego", "--config", str(config_path)])

        with pytest.raises(SystemExit, match=f"^{expected_rc}$"), _config_file(
            toml.dumps(config_content), config_path
        ):
            main()

        std_out, std_err = capfd.readouterr()
        assert std_out == expected_std_out
        assert std_err == expected_err_out


class TestConfigContainersFormat:
    @pytest.mark.parametrize(
        "config_content, expected_rc, expected_std_out, expected_std_err",
        [
            # Basic errors
            (
                {"docker_containers": 3},
                os.EX_CONFIG,
                "No any valid container configuration found\n",
                """errors detected in configured containers:
  - docker_containers should be represented by list, got int
""",
            ),
            (
                {"docker_containers": {}},
                os.EX_CONFIG,
                "No any valid container configuration found\n",
                """errors detected in configured containers:
  - docker_containers should be represented by list, got dict
""",
            ),
            (
                {"docker_containers": ["should be dict"]},
                os.EX_CONFIG,
                "No any valid container configuration found\n",
                """errors detected in configured containers:
  - docker_containers.0.*: ["must be represented by 'dict', got 'str'"]
""",
            ),
            # Errors, specific to Docker containers configuration
            (
                {
                    "docker_containers": [
                        {},
                        {
                            "name": 7,
                            "wrong_field": 12,
                            "docker_file_path": False,
                            "docker_image": [],
                            "docker_build_options": 0,
                        },
                        {
                            "name": "not slug",
                            "docker_file_path": "/tmp/Docker",
                            "docker_image": "python:3.9-alpine",
                            "docker_build_options": "-it",
                        },
                        {
                            "name": "cant_be_compose_and_image",
                            "docker_file_path": "/tmp/Docker",
                            "docker_compose_file_path": "/tmp/docker-compose.yaml",
                            "docker_build_options": "-it",
                        },
                    ]
                },
                os.EX_CONFIG,
                "No any valid container configuration found\n",
                """errors detected in configured containers:
  - docker_containers.0.*: ["one of the following fields must be present: \
['docker_compose_file_path', 'docker_compose_options', 'docker_file_path', 'docker_image']"]
  - docker_containers.0.name: ['mandatory field missing']
  - docker_containers.1.docker_build_options: ['should be of type str, got int']
  - docker_containers.1.docker_file_path: ['should be of type str, got bool']
  - docker_containers.1.docker_image: ['should be of type str, got list']
  - docker_containers.1.name: ['should be of type str, got int']
  - docker_containers.1.wrong_field: ['unsupported field']
  - docker_containers.2.docker_file_path: ["conflicting fields found: {'docker_image'}"]
  - docker_containers.2.docker_image: ["conflicting fields found: {'docker_file_path'}"]
  - docker_containers.2.name: \
["should consist only of letters, digits, '-', or '_', got 'not slug'"]
  - docker_containers.3.docker_compose_file_path: \
["requires following fields to be present as well, but they are not found: \
{'docker_compose_service'}", "conflicting fields found: {'docker_file_path'}"]
  - docker_containers.3.docker_file_path: ["conflicting fields found: {'docker_compose_file_path'}"]
""",
            ),
            # Errors, specific to Docker COMPOSE containers configuration
            (
                {
                    "docker_containers": [
                        {
                            "docker_compose_options": "--file docker-compose.yml",
                            "docker_compose_service": "client",
                        }
                    ]
                },
                os.EX_CONFIG,
                "No any valid container configuration found\n",
                """errors detected in configured containers:
  - docker_containers.0.docker_compose_service: ["requires following fields to be present \
as well, but they are not found: {'docker_compose_file_path'}"]
  - docker_containers.0.name: ['mandatory field missing']
""",
            ),
            (
                {
                    "docker_containers": [
                        {
                            "name": "test_compose_container",
                            "docker_compose_file_path": "docker-compose.yml",
                        }
                    ]
                },
                os.EX_CONFIG,
                "No any valid container configuration found\n",
                """errors detected in configured containers:
  - docker_containers.0.docker_compose_file_path: ["requires following fields to be present \
as well, but they are not found: {'docker_compose_service'}"]
""",
            ),
        ],
    )
    def test_nok_containers(
        self,
        capfd,
        monkeypatch,
        tmp_path,
        config_content,
        expected_rc,
        expected_std_out,
        expected_std_err,
    ):
        config_path = tmp_path / "cfg.toml"
        monkeypatch.setattr(sys, "argv", ["rego", "--config", str(config_path), "--containers"])

        with pytest.raises(SystemExit, match=f"^{expected_rc}$"), _config_file(
            toml.dumps(config_content), config_path
        ):
            main()

        std_out, std_err = capfd.readouterr()
        assert std_out == expected_std_out
        assert std_err == expected_std_err


class BaseCommandsTest:
    """
    These tests might be overcomplicated. I don't know how to do it better.
    We have too many scenarios to cover. Copy-pasting simple tests many times
    might be even more annoying and error-prone.

    Commands can be executed with rego in 4 different environments:
    - natively, directly on host machine
    - in locally built container
    - in container based on repo image
    - in docker compose service

    In all cases we should support the same:
    - set of ways how command can be configured
    - way of handling command options
    To check this part we use parametrized fixtures in parent class.

    However for different environments we expect different subprocess calls
    and different set of additional sections in config file.
    To check this part we use subclass-specific parametrized fixtures.
    """

    BASE_COMMAND_CFG: dict = {}

    COMMON_COMMANDS_TEMPLATES = [
        # Simple command
        {"execute": "echo PASSED"},
        # before/after
        {
            "before": ["echo BEFORE", "echo TEST"],
            "execute": "echo PASSED",
            "after": ["echo done"],
        },
    ]

    def fxtc_command(self, request):
        raise NotImplementedError("should be implemented by subclasses")

    @pytest.fixture(
        scope="class",
        params=[
            [],
            ["-al"],
        ],
    )
    def fxtc_run_options(self, request):
        yield request.param

    @pytest.fixture(scope="class")
    def fxtc_env_specific_data(self) -> List[str]:
        raise NotImplementedError("should be implemented by subclasses")

    def expected_calls(self, command: dict, run_options: List[str], config_overrides: dict):
        raise NotImplementedError("should be implemented by subclasses")

    @staticmethod
    def _generate_command_to_run(command_cfg: dict, command_options: List[str]) -> List[str]:
        before = command_cfg.get("before", [])
        after = command_cfg.get("after", [])

        execute = " ".join([command_cfg["execute"]] + command_options)

        return ["/bin/sh", "-c", f"{' && '.join(before + [execute] + after)}"]

    @staticmethod
    def _write_config_and_run_command(
        argv_patcher,
        expected_rc,
        command_config: dict,
        name_of_command_to_run: str,
        config_overrides: dict,
        run_options: List[str],
        tmp_path: pathlib.Path,
        capfd: pytest.CaptureFixture,
    ):
        config_path = tmp_path / "cfg.toml"
        config_content = {"commands": [command_config]}
        config_content.update(config_overrides)

        what_to_run = [
            "rego",
            "-d",
            "--config",
            str(config_path),
            name_of_command_to_run,
        ] + run_options

        argv_patcher.setattr(sys, "argv", what_to_run)

        with pytest.raises(SystemExit, match=expected_rc), _config_file(
            toml.dumps(config_content), config_path
        ):
            main()

        return capfd.readouterr()

    @patch("rego.subprocess.run")
    def test_ok(
        self,
        patched_run,
        capfd,
        monkeypatch,
        tmp_path,
        fxtc_command: dict,
        fxtc_env_specific_data: dict,
        fxtc_run_options: List[str],
    ):
        patched_run.return_value.returncode = 0
        expected_calls = self.expected_calls(fxtc_command, fxtc_run_options, fxtc_env_specific_data)

        std_out, std_err = self._write_config_and_run_command(
            argv_patcher=monkeypatch,
            expected_rc=_OK_EXIT_CODE_REGEX,
            command_config=fxtc_command,
            name_of_command_to_run=fxtc_command["name"],
            config_overrides=fxtc_env_specific_data.get("config_overrides", {}),
            run_options=fxtc_run_options,
            tmp_path=tmp_path,
            capfd=capfd,
        )

        assert std_err == ""

        assert patched_run.call_count == len(expected_calls)
        for expected_call in expected_calls:
            expected_kwargs = {}
            if isinstance(expected_call, tuple):
                expected_kwargs = expected_call[1]
                expected_call = expected_call[0]

            assert f"[DEBUG] running: {expected_call}" in std_out
            patched_run.assert_has_calls(calls=[call(expected_call, **expected_kwargs)])


class TestNativeCommands(BaseCommandsTest):
    BASE_COMMAND_CFG: dict = {
        "name": "test_cmd",
        "description": "-",
    }

    @pytest.fixture(
        scope="class",
        params=BaseCommandsTest.COMMON_COMMANDS_TEMPLATES,
    )
    def fxtc_command(self, request):
        yield {**self.BASE_COMMAND_CFG, **request.param}

    @pytest.fixture(scope="class")
    def fxtc_env_specific_data(self):
        # Native commands are simple and to test them we don't need
        # any additional config sections, or test hints.
        yield {}

    def expected_calls(self, command: dict, run_options: List[str], config_overrides: dict):
        return [self._generate_command_to_run(command, run_options)]

    @pytest.mark.parametrize(
        "command_config, expected_rc, expected_std_out, expected_std_err",
        [
            (
                {
                    "name": "native",
                },
                os.EX_CONFIG,
                ["command 'native' is not present in the config\n"],
                [
                    "errors detected in 'commands' configurations",
                    "(probably this is the reason why command can't be found):",
                    "  - commands.0.description: ['mandatory field missing']",
                    "  - commands.0.execute: ['mandatory field missing']",
                ],
            ),
            (
                {
                    "name": "other_cmd",
                    "description": "-",
                    "execute": "echo OK",
                },
                os.EX_UNAVAILABLE,
                ["command 'native' is not present in the config\n"],
                [],
            ),
            (
                {
                    "name": "native",
                    "description": "-",
                    "execute": "boolsheet",
                },
                127,
                [],
                ["/bin/sh: boolsheet: not found\n"],
            ),
            (
                {
                    "name": "native",
                    "description": "-",
                    "execute": "/bin/sh 'syntax wrong",
                },
                2,
                [],
                ["/bin/sh: syntax error: unterminated quoted string\n"],
            ),
        ],
    )
    def test_nok(
        self,
        capfd,
        monkeypatch,
        tmp_path,
        command_config,
        expected_rc,
        expected_std_out,
        expected_std_err,
    ):
        std_out, std_err = self._write_config_and_run_command(
            argv_patcher=monkeypatch,
            expected_rc=f"^{expected_rc}$",
            command_config=command_config,
            name_of_command_to_run="native",
            config_overrides={},
            run_options=[],
            tmp_path=tmp_path,
            capfd=capfd,
        )
        for expected_line in expected_std_out:
            assert expected_line in std_out

        for expected_line in expected_std_err:
            assert expected_line in std_err


class TestLocallyBuiltContainerCommands(BaseCommandsTest):
    BASE_COMMAND_CFG: dict = {
        "name": "test_cmd",
        "description": "-",
        "docker_container": "test_docker_file",
    }

    @pytest.fixture(
        scope="class",
        params=BaseCommandsTest.COMMON_COMMANDS_TEMPLATES
        + [
            {
                "execute": "ls",
                "docker_run_options": "-it -v .:/app -w /app --user 1000:1000",
            },
        ],
    )
    def fxtc_command(self, request):
        yield {**self.BASE_COMMAND_CFG, **request.param}

    @pytest.fixture(
        scope="class",
        params=[
            # Relative path to dockerfile, no build overrides
            {
                "config_overrides": {
                    "docker_containers": [
                        {
                            "name": "test_docker_file",
                            "docker_file_path": "Dockerfile_test",
                        }
                    ],
                },
                "test_helpers": {
                    "expected_build_options": [
                        "--file",
                        "Dockerfile_test",
                        "--tag",
                        "test_docker_file-for-app",
                    ],
                    "expected_tag": "test_docker_file-for-app",
                },
            },
            # Absolute path to dockerfile with build overrides
            {
                "config_overrides": {
                    "docker_containers": [
                        {
                            "name": "test_docker_file",
                            "docker_file_path": "/absolute/path/Dockerfile_test",
                            "docker_build_options": "--tag test_tag -f Dockerfile_override",
                        }
                    ],
                },
                "test_helpers": {
                    "expected_build_options": ["--tag", "test_tag", "-f", "Dockerfile_override"],
                    "expected_tag": "test_tag",
                },
            },
            # Format of 'docker_build_options' is wrong (exact value for override option
            # is not provided), we should use default value in this case.
            # We don't perform deep inspection of options, provided in config,
            # this mean that this may lead to ugly resulting command, but it is probably
            # out of our responsibility.
            {
                "config_overrides": {
                    "docker_containers": [
                        {
                            "name": "test_docker_file",
                            "docker_file_path": "Dockerfile_test",
                            "docker_build_options": "--tag",
                        }
                    ],
                },
                "test_helpers": {
                    "expected_build_options": [
                        "--file",
                        "Dockerfile_test",
                        "--tag",
                        "test_docker_file-for-app",
                        "--tag",
                    ],
                    "expected_tag": "test_docker_file-for-app",
                },
            },
        ],
    )
    def fxtc_env_specific_data(self, request):
        yield request.param

    def expected_calls(self, command: dict, run_options: List[str], env_specific_data: dict):
        docker_run_options_str = command.get("docker_run_options", "")
        helpers = env_specific_data["test_helpers"]

        build_command = (
            ["docker", "build", "."] + helpers["expected_build_options"],
            {"stdout": subprocess.DEVNULL},
        )
        run_command = (
            ["docker", "run", "--quiet", "-e", "REGO_CONTAINER_NAME=test_docker_file"]
            + docker_run_options_str.split()
            + [helpers["expected_tag"]]
            + self._generate_command_to_run(command, run_options)
        )

        return [build_command, run_command]


class TestContainerFromImageCommands(BaseCommandsTest):
    BASE_COMMAND_CFG: dict = {
        "name": "test_cmd",
        "description": "-",
        "docker_container": "test_image_from_repo",
    }

    @pytest.fixture(
        scope="class",
        params=BaseCommandsTest.COMMON_COMMANDS_TEMPLATES
        + [
            {
                "execute": "ls",
                "docker_run_options": "-it -v .:/app -w /app --user 1000:1000",
            },
        ],
    )
    def fxtc_command(self, request):
        yield {**self.BASE_COMMAND_CFG, **request.param}

    @pytest.fixture(
        scope="class",
        params=[
            {
                "config_overrides": {
                    "docker_containers": [
                        {
                            "name": "test_image_from_repo",
                            "docker_image": "python:3.9-alpine",
                        }
                    ],
                },
            },
        ],
    )
    def fxtc_env_specific_data(self, request):
        yield request.param

    def expected_calls(self, command: dict, run_options: List[str], env_specific_data: dict):
        docker_run_options_str = command.get("docker_run_options", "")
        container_config = env_specific_data["config_overrides"]["docker_containers"][0]

        run_command = (
            ["docker", "run", "--quiet", "-e", "REGO_CONTAINER_NAME=test_image_from_repo"]
            + docker_run_options_str.split()
            + [container_config["docker_image"]]
            + self._generate_command_to_run(command, run_options)
        )

        return [run_command]


class TestDockerComposeServiceCommands(BaseCommandsTest):
    BASE_COMMAND_CFG: dict = {
        "name": "test_cmd",
        "description": "-",
        "docker_container": "test_docker_compose",
    }

    @pytest.fixture(
        scope="class",
        params=BaseCommandsTest.COMMON_COMMANDS_TEMPLATES
        + [
            {
                "execute": "ls",
                "docker_run_options": "-it -v .:/app -w /app --user 1000:1000",
            },
        ],
    )
    def fxtc_command(self, request):
        yield {**self.BASE_COMMAND_CFG, **request.param}

    @pytest.fixture(
        scope="class",
        params=[
            {
                "config_overrides": {
                    "docker_containers": [
                        {
                            "name": "test_docker_compose",
                            "docker_compose_file_path": "docker-compose.yml",
                            "docker_compose_service": "client",
                        }
                    ],
                },
                "test_helpers": {
                    "expected_docker_compose_options": ["--file", "docker-compose.yml"],
                    "expected_docker_compose_file": "docker-compose.yml",
                },
            },
            # Override docker_compose_options.
            {
                "config_overrides": {
                    "docker_containers": [
                        {
                            "name": "test_docker_compose",
                            "docker_compose_file_path": "docker-compose.yml",
                            "docker_compose_service": "client",
                            "docker_compose_options": "--file override-docker-compose.yml",
                        }
                    ],
                },
                "test_helpers": {
                    "expected_docker_compose_options": ["--file", "override-docker-compose.yml"],
                    "expected_docker_compose_file": "override-docker-compose.yml",
                },
            },
            # Wrong override options (--file without value)
            {
                "config_overrides": {
                    "docker_containers": [
                        {
                            "name": "test_docker_compose",
                            "docker_compose_file_path": "docker-compose.yml",
                            "docker_compose_service": "client",
                            "docker_compose_options": "--file",
                        }
                    ],
                },
                "test_helpers": {
                    "expected_docker_compose_options": ["--file", "docker-compose.yml", "--file"],
                    "expected_docker_compose_file": "docker-compose.yml",
                },
            },
        ],
    )
    def fxtc_env_specific_data(self, request):
        yield request.param

    def expected_calls(self, command: dict, run_options: List[str], env_specific_data: dict):
        docker_run_options_str = command.get("docker_run_options", "")
        container_config = env_specific_data["config_overrides"]["docker_containers"][0]
        expected_docker_compose_options = env_specific_data["test_helpers"][
            "expected_docker_compose_options"
        ]
        expected_docker_compose_file = env_specific_data["test_helpers"][
            "expected_docker_compose_file"
        ]

        run_command = (
            [
                "docker",
                "compose",
                "--progress",
                "quiet",
                *expected_docker_compose_options,
                "run",
            ]
            + docker_run_options_str.split()
            + [container_config["docker_compose_service"]]
            + self._generate_command_to_run(command, run_options)
        )

        clean_up_commands = [
            (["docker", "compose", "down", "--remove-orphans"], {"stdout": subprocess.DEVNULL}),
            (
                ["docker", "compose", "--file", expected_docker_compose_file, "rm", "-fsv"],
                {"stdout": subprocess.DEVNULL},
            ),
        ]

        return [run_command, *clean_up_commands]


class TestContainers:
    config_content = {
        "commands": [
            {
                "name": "command_without_container",
                "description": "-",
                "execute": "echo OK",
            },
            {
                "name": "command_with_default_container",
                "description": "-",
                "execute": "echo OK",
                "docker_container": "container1",
            },
        ],
        "docker_containers": [
            {
                "name": "container1",
                "docker_image": "container1image",
            },
            {
                "name": "container2",
                "docker_image": "container2image",
            },
        ],
    }

    @pytest.fixture(
        scope="class",
        params=["--container", "-c"],
    )
    def fxtc_container_option(self, request):
        yield request.param

    @pytest.fixture(
        scope="class",
        params=[0, 1],
    )
    def fxtc_container_to_test(self, request):
        yield self.config_content["docker_containers"][request.param]

    @pytest.fixture(scope="class")
    def fxtc_config_file(self, tmp_path_factory):
        config_path = tmp_path_factory.mktemp("test") / "cfg.toml"
        with open(config_path, "w") as toml_file:
            toml_file.write(toml.dumps(self.config_content))
        yield config_path

    def _expected_call(self, image_name: str, container_name: str):
        return [
            "docker",
            "run",
            "--quiet",
            "-e",
            f"REGO_CONTAINER_NAME={container_name}",
            image_name,
            "/bin/sh",
            "-c",
            "echo OK",
        ]

    def _what_to_run(self, container_options: List[str], config_file: pathlib.Path):
        return [
            "rego",
            "-d",
            *container_options,
            "--config",
            str(config_file),
            "command_without_container",
        ]

    @patch("rego.subprocess.run")
    def test_single_container(
        self,
        patched_run,
        capfd,
        monkeypatch,
        fxtc_config_file,
        fxtc_container_option,
        fxtc_container_to_test,
    ):
        patched_run.return_value.returncode = 0

        container_name = fxtc_container_to_test["name"]
        image_name = fxtc_container_to_test["docker_image"]

        what_to_run = self._what_to_run([fxtc_container_option, container_name], fxtc_config_file)
        monkeypatch.setattr(sys, "argv", what_to_run)
        expected_calls = [self._expected_call(image_name, container_name)]

        with pytest.raises(SystemExit, match=_OK_EXIT_CODE_REGEX):
            main()

        out, err = capfd.readouterr()
        assert err == ""
        assert patched_run.call_count == len(expected_calls)
        for expected_call in expected_calls:
            assert f"[DEBUG] running: {expected_call}" in out
            patched_run.assert_has_calls(calls=[call(expected_call)])

    @patch("rego.subprocess.run")
    def test_multiple_containers(
        self,
        patched_run,
        capfd,
        monkeypatch,
        fxtc_config_file,
        fxtc_container_option,
    ):
        patched_run.return_value.returncode = 0

        container1, container2 = self.config_content["docker_containers"]

        what_to_run = self._what_to_run(
            [fxtc_container_option, container1["name"], fxtc_container_option, container2["name"]],
            fxtc_config_file,
        )
        monkeypatch.setattr(sys, "argv", what_to_run)
        expected_calls = [
            self._expected_call(image_name=c["docker_image"], container_name=c["name"])
            for c in self.config_content["docker_containers"]
        ]

        with pytest.raises(SystemExit, match=_OK_EXIT_CODE_REGEX):
            main()

        out, err = capfd.readouterr()
        assert err == ""
        assert patched_run.call_count == len(expected_calls)
        for expected_call in expected_calls:
            assert f"[DEBUG] running: {expected_call}" in out
            patched_run.assert_has_calls(calls=[call(expected_call)])

    @patch("rego.subprocess.run")
    def test_all_containers(
        self,
        patched_run,
        capfd,
        monkeypatch,
        fxtc_config_file,
        fxtc_container_option,
    ):
        patched_run.return_value.returncode = 0

        what_to_run = self._what_to_run([fxtc_container_option, "*"], fxtc_config_file)
        monkeypatch.setattr(sys, "argv", what_to_run)
        expected_calls = [
            self._expected_call(image_name=c["docker_image"], container_name=c["name"])
            for c in self.config_content["docker_containers"]
        ]

        with pytest.raises(SystemExit, match=_OK_EXIT_CODE_REGEX):
            main()

        out, err = capfd.readouterr()
        assert err == ""
        assert patched_run.call_count == len(expected_calls)
        for expected_call in expected_calls:
            assert f"[DEBUG] running: {expected_call}" in out
            patched_run.assert_has_calls(calls=[call(expected_call)])
