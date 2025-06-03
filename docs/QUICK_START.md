# Quick Start

## 0. Requirements.

runo was designed to work without any dependencies, 
requiring installation of additional components. 
It needs only 1 (or 2) thing(s), which is/are almost 100% available
on any development machine by default nowadays:
- Python of any version, starting from Python3.6,
- OPTIONALLY: Docker and/or docker compose (depends on your needs).

Actually, you can start even without docker, if your repo doesn't use it.
Docker is not needed for `runo` itself, but `runo` may run docker commands,
if you will ask it. If you don't have anything, what should use docker,
then it is not needed for `runo` as well.

## 1. Integrate `runo` into your repository.

Just copy [runo file](../runo) to root of your repository and make it executable
```
> cd <root of your repo>
> wget https://raw.githubusercontent.com/frwl404/runo/refs/heads/master/runo
> chmod 755 runo
```
This way any new contributor will not need to install anything - everything is already in your repo.  
At this moment you don't have any commands configured:
```
> ./runo 
Config is not created yet.
Please initialize it with './runo --init'
```

## 2. Ask runo to generate initial config.

```
> ./runo --init
config created: runo.toml
```

Now you will see commands, suggested by runo by default:
```
> ./runo
Following commands are available:
  * test - runs unit tests ['./runo tests --cov -vv', './runo tests --last-failed']
  * build - builds the project ['./runo build']
  * shell - debug container by running shell in interactive mode (keep container running) ['./runo shell']
  * pre-commit - quick checks/fixes of code formatting (ruff/mypy) ['./runo pre-commit']
  * update-deps - updates dependencies, used in project, to the latest versions ['./runo update-deps']
```
At this moment most part of them are just a mocks, which prints something to console,
because at this moment `./runo` doesn't know what `test`/`build`/`...` means for your project.
Only `./runo shell` do exactly what you expect from it (because it is quite universal thing, which means the same in any repo/project).

## 3. Adopt generated config for your needs.

This is the part where all magic is. 
With help of simple config you hide all complexity and peculiarities 
of your repo and let `runo` translate it to very simple,
clean and unified interface

In auto-generated `runo.toml` you will already find quite detailed examples,
explaining configuration of `commands` and `containers` (config uses only these 
2 types of objects), but most detailed information can be found [here](CONFIG.md)

