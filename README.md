# A single-file tool that takes care of local dev environment.

## 🔍 Problem: nowadays, every repo has its own development workflow
When switching to a new repository, one of the first questions is: 
*"How do I run build/lint/tests/... here?"*  

Good repositories have documentation, explaining the procedure. 
Ideally, they use **Docker**, so you don’t need to install anything, 
but need to know right commands to start with. 
However, the next repository you work on, will likely have a 
**different** process - maybe also Docker-based, but still different.  

**The result:**
- Constantly learning/developing different workflows slows you down;
- Workflow, designed from scratch, might be very far from optimal;
- Might be needed to install different SW from repo to repo;
- Too complex/unusual workflow may scare away new contributors.


## ✅ Solution: `dev-it-easy`
Imagine you could enter **any repo** and immediately know **what** can be done and **how** to do it.  
With `dev-it-easy`, just run:  
```
> ./dev
Following commands are available:
  * test - runs unit tests (pytest) ['./dev tests --cov -vv', './dev tests --last-failed']
  * build - builds the project ['./dev build']
  * shell - debug container by running shell in interactive mode (keep container running) ['./dev shell']
  * pre-commit - quick checks/fixes of code formatting (ruff/mypy) ['./dev pre-commit']
  * update-deps - updates dependencies, used in project, to the latest versions ['./dev update-deps']
```

You immediately see **WHAT** can be done in this repo and **HOW** it can be done.  
Now, running build is as simple as:
```
> ./dev build
Buld is running
done
```

## 🔀 Cross-Platforming
But what if you want to perform build/tests/... for different platforms? 
Not a problem, just ask the tool to show all available containers and run
command in any of them as easy as that:
```
> ./dev --containers
Following containers are available:
  * Debian
  * Centos
  * RockyLinux

> ./dev -c Debian build
Buld for Debian is running
done
```

or you can run command in all available containers:
```
> ./dev -c "*" test
Running test for Debian
PASSED
Running test for Centos
PASSED
Running test for RockyLinux
PASSED
```

## 🎯 Why use "dev-it-easy"?
- Standardized workflow across different repositories
- Zero installation (just add 1 file to your repo)
- Works across multiple platforms effortlessly

## 🚀 Quick start.

Follow [this short instruction](docs/QUICK_START.md) to integrate dev into your project.  
In case of some problems, please feel free to contact author:
- Email: anton.chivkunov@gmail.com

