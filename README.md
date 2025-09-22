# Hooked

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)

## Installation

Install this package directly from this repository using pip:

```bash
pip install --no-cache-dir  --force-reinstall  git+https://github.com/conmob-devsecops/hooked.git@test/installer
```

After `hooked` is available on your `PATH`, you can run:

```bash
hooked install [path-to-rule-set-repository]
```

For now, the only file that must be present in the rule set repository is a valid `.pre-commit-config.yaml` file.

See this repository for an example rule
set: [conmob-devsecops/hooked-rules](https://github.com/conmob-devsecops/hooked-ruleset-tsi),
the branch checked out by default is the default one, if not specified otherwise with the `--branch` option.

```bash
hooked install git@github.com:conmob-devsecops/hooked-ruleset-tsi.git --branch=feature/new-rule
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

## Keeping up to date

### Rules

To update the ruleset repository, run:

```bash
hooked update-rules
```

### Hooked

To update `hooked` itself, run:

```bash
hooked ugrade
```

Or you can the built-in update command, see `--help` for more information:

```bash
pip install --no-cache-dir  --force-reinstall  git+https://github.com/conmob-devsecops/hooked.git@test/installer#
```

(Same command as installation)

`hooked` internally runs `hooked upgrade --periodic` from time to time to check for updates, so you don't have to worry about
it. If there are newer versions available, it will automatically update itself and the ruleset repository.

## Uninstall

To uninstall `hooked` and remove the global git hooks, run:

```bash
hooked uninstall
```

This will remove the global git hooks and uninstall `pre-commit` from your local repository if it was installed by
`hooked`.

## Configuration

## Environment variables

`HOOKED_SKIP_UPGRADE_CHECK`: If set to any value, disables the automatic upgrade check that runs sometimes.
`HOOKED_LOG_LEVEL`: Sets the logging level.

Currently, the uninstallation script removes all hooks installed by `hooked` and unsets the global Git template
directory,
but repositories that already had local `pre-commit` hooks installed will not be affected. You may need to manually
remove
hooks from `.git/hooks` if necessary.
