# Quick Start

## 0. Requirements.

Rego was designed to work without any dependencies, 
requiring installation of additional components. 
It needs only 1 (or 2) thing(s), which is/are almost 100% available
on any development machine by default nowadays:
- Python of any version, starting from Python3.6,
- OPTIONALLY: Docker and/or docker compose (depends on your needs).

Actually, you can start even without docker, if your repo doesn't use it.
Docker is not needed for `dev` itself, but `dev` may run docker commands,
if you will ask it. If you don't have anything, what should use docker,
then it is not needed for `dev` as well.

## 1. Integrate `dev` into your repository.

Just copy [dev file](../dev) to root of your repository and make it executable
```
> cd <root of your repo>
> wget https://github.com/frwl404/dev/raw/refs/heads/main/dev
> chmod 755 dev
```
This way any new contributor will not need to install anything - everything is already in your repo.  
At this moment you don't have any commands configured:
```
> ./dev 
Config is not created yet.
Please initialize it with './dev --init'
```

## 2. Ask dev to generate initial config.

```
> ./dev --init
config created: dev.toml
```

Now you will see commands, suggested by dev by default:
```
> ./dev
Following commands are available:
  * test - runs unit tests ['./dev tests --cov -vv', './dev tests --last-failed']
  * build - builds the project ['./dev build']
  * shell - debug container by running shell in interactive mode (keep container running) ['./dev shell']
  * pre-commit - quick checks/fixes of code formatting (ruff/mypy) ['./dev pre-commit']
  * update-deps - updates dependencies, used in project, to the latest versions ['./dev update-deps']
```
At this moment most part of them are just a mocks, which prints something to console,
because at this moment `./dev` doesn't know what `test`/`build`/`...` means for your project.
Only `./dev shell` do exactly what you expect from it (because it is quite universal thing, which means the same in any repo/project).

## 3. Adopt generated config for your needs.

This is the part where all magic is. 
With help of simple config you hide all complexity and peculiarities 
of your repo and let `dev` translate it to very simple,
clean and unified interface

In auto-generated `dev.toml` you will already find quite detailed examples,
explaining configuration of `commands` and `containers` (config uses only these 
2 types of objects), but most detailed information can be found [here](CONFIG.md)

