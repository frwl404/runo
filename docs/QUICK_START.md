# Quick Start

## 0. Requirements.

`runo` was designed to work without any dependencies, 
requiring installation of additional components. 
It needs only 1 (or 2) things, which are almost certainly available
on any development machine by default nowadays:
- Python of any version, starting from Python 3.6,
- OPTIONALLY: Docker and/or docker compose (depends on your needs).  
  Docker is not needed for `runo` itself, but `runo` may run docker commands,
  if you will ask it.  
  If you don't have anything, what should use docker, then it is not needed.

## 1. Integrate `runo` into your repository.

Go to root of your repository and do one of two things:
<details>
<summary>Just copy file directly to you repo (and make it executable)</summary>

```
wget https://raw.githubusercontent.com/frwl404/runo/refs/heads/master/runo &&\
chmod 755 runo
```
</details>

<details>
<summary>Add as submodule</summary>

```
git submodule add git@github.com:frwl404/runo.git .runo &&\
ln -s .runo/runo runo
```
</details>

Both ways any new contributor will not need to install anything - 
everything is already in your repo, yet in second case they will also
need to load submodule(s) with `git submodule update --init`.  
I personally prefer first method.

At this moment you already can run `runo`, but don't have 
any commands configured yet:
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

