# Single-file tool that greatly simplifies the development workflow for any repository.

[![CI](https://github.com/frwl404/dev-it-easy/actions/workflows/ci.yml/badge.svg?event=push)](https://github.com/frwl404/dev-it-easy/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/frwl404/runo/branch/master/graph/badge.svg)](https://app.codecov.io/gh/frwl404/runo)
![Static Badge](https://img.shields.io/badge/supported_python-from_3.6_to_3.13-limegreen)

## 🔍 Problem: nowadays, every repo has its own development workflow
When switching to a new repository, one of the first questions would be: 
*"How to run build/lint/tests/... here?"*  

Good repositories have documentation, explaining the procedure. 
Ideally, they use **Docker**, so you don’t need to install anything, 
but need to know right commands to start with. 
However, the next repository you work on, will likely have a **different** 
process - maybe also Docker-based, but still different.

**The result:**
- Constantly learning/developing different workflows slows you down;
- Workflow, designed from scratch, might be very far from optimal;
- Might be needed to install different SW from repo to repo;
- Too complex/unusual workflow may scare away new contributors.

NOOOOOO

## ✅ Solution: `runo`
Imagine you could enter **any repo** and immediately know **what** can 
be done and **how** to do it. With `runo`, just run:  
```
> ./runo
Following commands are available:
  * test - runs unit tests (pytest) ['./runo tests --cov -vv', './runo tests --last-failed']
  * build - builds the project ['./runo build']
  * shell - debug container by running shell in interactive mode (keep container running) ['./runo shell']
  * pre-commit - quick checks/fixes of code formatting (ruff/mypy) ['./runo pre-commit']
  * update-deps - updates dependencies, used in project, to the latest versions ['./runo update-deps']
```

You immediately see **WHAT** can be done in this repo and **HOW** it can be done.  
Now, running build is as simple as:
```
> ./runo build
Buld is running
done
```

## 🔀 Cross-Platforming
But what if you want to perform build/tests/... for different platforms? 
Not a problem, just ask `runo` to show all available containers and run
command in any of them as easy as that:
```
> ./runo --containers
Following containers are available:
  * Debian
  * Centos
  * RockyLinux

> ./runo -c Debian build
Buld for Debian is running
done
```

or you can run command in all available containers:
```
> ./runo -c "*" test
Running test for Debian
PASSED
Running test for Centos
PASSED
Running test for RockyLinux
PASSED
```

## 🎯 Why use runo?
- Standardized workflow across different repositories
- Zero installation (just add 1 file to your repo)
- `runo` needs only Python, which is present almost everywhere nowadays.
- Works across multiple platforms effortlessly

## 🚀 Quick start.

Follow [this short instruction](docs/QUICK_START.md) to integrate runo into your project.  
In case of some problems, please feel free to contact author:
- Email: anton.chivkunov@gmail.com  

_*If you are open-source project, hosted on github.com, want to try `runo`, but
don't have enough time for integration, please contact me - I can prepare
integration PR for your repo and you will need just to check how well it works 
for you._

