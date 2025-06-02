# `runo` Config File Reference

## Table of content
- [Introduction](#introduction)
- [Commands](#commands)
- - [Mandatory fields](#mandatory-fields)
- - - [name](#name-string)
- - - [description](#description-string)
- - - [execute](#execute-string)
- - [Optional fields](#optional-fields)
- - - [before](#before-liststring)
- - - [after](#after-liststring)
- - - [docker_container](#docker_container-string)
- - - [docker_run_options](#docker_run_options-string)
- [Containers](#containers)
- - [Containers, based on images from repo](#containers-based-on-images-from-repo),
- - [Containers, based on images, built locally with `Dockerfile`](#containers-based-on-images-built-locally-with-dockerfile)
- - [Docker compose containers](#docker-compose-containers).

## Introduction

`runo` config is a regular `.toml` file, which is needed to let `runo` know: 
1) Which commands you want to see in your repo (`build`/`test`/`...`),
2) Which docker containers are going to be used by commands in your project.
3) What every command means exactly. For example, for one project `test` command may mean:  
"_run `pytest --cov` in `python3:latest` container_".  
For another project it may mean:  
"_run `go test` in `app` container of `docker-compose.yml`_"

Therefore, `runo` config contains 2 lists of objects: 
[commands](#commands) and [containers](#containers), which we will discuss in details in the next 2 sections.

## Commands

Configuration of every command consists of several simple  fields.  
First, few examples, and then we will discuss details.
- Simplest case: command config uses only mandatory fields:
```toml
[[commands]]
name = "e2e"
description = "run end to end tests"
execute = "python3 -m tests.e2e.run"
```
 - Most complex case: command config uses all possible fields:
```toml
[[commands]]
name = "test"
description = "runs unit tests"
before = ["echo This is just an exampe", "echo You should configure your tests here"]
execute = "pytest"
after =["echo done > /dev/null"]
examples = ["tests --cov -vv", "tests --last-failed"]
docker_container = "alpine"
docker_run_options = "-it -v .:/app -w /app"
```

Now let's discuss all parameters in details.

### Mandatory fields.

Configuration of `runo` commands is quite simple and contains only 3 mandatory fields:

#### `name` (`string`)

This is identifier of the command, which should be short, but **unique** 
and consist only of letters, digits, `-`, or `_` symbols.  
Examples: `test`, `build`, `make`, `...`  

#### `description` (`string`)

Short, but meaningful description of the command, 
which will be shown as help message to user. Examples:
- _"runs unit tests (pytest)"_,
- _"runs unit tests (go test)"_,
- _"builds the project"_.

#### `execute` (`string`)

Main part of the command. It is `shell` command or script, 
which will be executed by `runo` under the hood (inside container 
or natively). Examples:
- `./scripts/build.sh`,
- `go test`,
- `pytest`,

All arguments, which you will pass to command via CLI,
will be forwarded by `runo` to this `execute` instruction.
For example, if you have the following runo command: 
```toml
[[commands]]
name = "test"
description = "runs unit tests"
execute = "pytest --cov"
```
and will run it in the following way:
```
> ./runo test --pdb
```
then resulting command, which will be executed by `runo` will be: `pytest --cov --pdb`,

### Optional fields.

#### `before` (`list[string]`)

Before executing the main part, you may want to perform some setup 
(activate `venv` in case of Python project). In this section you can 
specify list of commands/scripts, which should be executed before 
the main part. Example:
- `["source /tmp/.venv/bin/activate", "echo Starting tests"]`


#### `after` (`list[string]`)

Similar to `before`, but executed after the main part. Example:
- `["rm -f /tmp/unneeded_files*"]`

Please note that these command are executed on host machine (not inside container).

#### `docker_container` (`string`)

Name of the container (defined in the same config), which should be used 
by the command by default. It can be overwritten via CLI at moment of run 
with help of `-c`/`--container` option.

#### `docker_run_options` (`string`)

Usually you want to use some `docker run` options when executing command 
(mount dir with your repo inside container, or something else). 
This field instruct `runo` to pass corresponding options to `run` command 
of corresponding container. Please refer to the 
[official docker documentation](https://docs.docker.com/reference/cli/docker/container/run/) 
to see what can be used here.


## Containers

While you can run `runo` command natively on your OS, 
most typical scenario would be to do it in some docker container. 
With `runo` you will configure it only once and then will not need 
to worry about container builds, tags, options and so on - `runo` will handle it.  
3 types of Docker containers are supported (if some other needed, please let me know):
- [Containers, based on images from repo](#containers-based-on-images-from-repo),
- [Containers, based on images, built locally with `Dockerfile`](#containers-based-on-images-built-locally-with-dockerfile)
- [Docker compose containers](#docker-compose-containers).

### Containers, based on images from repo

This is the simplest case. For such containers it is enough to specify: 
- `name`: unique identifier of container for runo,
- `docker_image`: name of the repo image, which should be used for this container

Example:

```toml
[[docker_containers]]
name = "alpine"
docker_image = "alpine:3.14"
```

### Containers, based on images, built locally with `Dockerfile`

This case is a bit more difficult, but more popular as well.
Here you will need to specify:
- `name`: unique identifier of container for runo,
- `docker_file_path`: relative or absolute path to `Dockerfile`, which should be used for container build, 
- `docker_build_options`: this one is **OPTIONAL**. 
You can instruct runo to use any option, which is supported in 
[official docker documentation](https://docs.docker.com/reference/cli/docker/buildx/build/).  

*Please note that providing `tag` in `docker_build_options` is not mandatory. 
When missing, `runo` will generate it automatically in format `<container name>-for-<repo name>`.

Example:

```toml
[[docker_containers]]
name = "python39"
docker_file_path = "containers/python39/Dockerfile"
docker_build_options = "--tag img-defined-by-docker-file"
```

### Docker compose containers.

This is most complex, but probably most popular case.
Here you will need to specify:
- `name`: unique identifier of container for runo,
- `docker_compose_file_path`: relative or absolute path to `docker-compose.yml`, 
- `docker_compose_service`: name of the service/container from docker compose file, which should be used for commands execution.
- `docker_compose_options`: this one is **OPTIONAL**. You can instruct runo to use any option, which is supported in 
[official docker documentation](https://docs.docker.com/reference/cli/docker/compose/).  

Example:

```toml
[[docker_containers]]
name = "app-with-db"
docker_compose_file_path = "docker-compose.yml"
docker_compose_service = "app"
docker_compose_options = "--all-resources"
```