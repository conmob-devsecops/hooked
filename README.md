# Hooked

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)

## Installation

Install this package directly from this repository using pip:

```bash
pip install git+git@github.com:conmob-devsecops/hooked.git
```

After `hooked` is available on your `PATH`, you can run:

```bash
hooked install --rules=[path-to-rule-set-repository]
```

For now, the only file that must be present in the rule set repository is a valid `.pre-commit-config.yaml` file.

See this repository for an example rule
set: [conmob-devsecops/hooked-rules](https://github.com/conmob-devsecops/hooked-ruleset-tsi),
the branch checked out by default is the default one, if not specified otherwise with the `--branch` option.

```bash
hooked install --rules=git+https://github.com/conmob-devsecops/hooked-ruleset-tsi --branch=feature/new-rule
```

### Local installation

If you want to install `hooked` in a local virtual environment instead of globally, you can use `hooked` as a local
module.

Clone the repository and navigate to the directory:

```bash
PYTHONPATH=src
python -m hooked [...]
```

## Usage

`hooked` automatically configures your local environment to use the global git hooks and takes about installing
local `pre-commit` hooks if repository contains a valid `.pre-commit-config.yaml` file.

## Uninstallation

To uninstall `hooked` and remove the global git hooks, run:

```bash
hooked uninstall
```

This will remove the global git hooks and uninstall `pre-commit` from your local repository if it was installed by
`hooked`.

Currently, the uninstallation script removes all hooks installed by `hooked` and unsets the global Git template
directory,
but repositories that already had local `pre-commit` hooks installed will not be affected. You may need to manually
remove
hooks from `.git/hooks` if necessary.
