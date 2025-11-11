# Installation

Hooked is usually installed via [pip](https://github.com/pypa/pip).

```bash
pip install git+https://github.com/conmob-devsecops/hooked.git@main
```

## MacOS

If you installed Python and pip via homebrew you will face the following error:

```bash
error: externally-managed-environment

× This environment is externally managed
╰─> To install Python packages system-wide, try brew install
    xyz, where xyz is the package you are trying to
    install.
```

As we don't have plans to either publish hooked via homebrew or pypa, we suggest
you to use [pipx](https://github.com/pypa/pipx) in this case.

```bash
# install pipx
brew install pipx

# install hooked with pipx
pipx install git+https://github.com/conmob-devsecops/hooked.git@main

# check if hooked is installed
pipx list
hooked version

# uninstall hooked
pipx uninstall hooked
```

## Windows

tba
