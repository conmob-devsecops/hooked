<p align=center>
  <img src="./docs/logo.svg" alt="HOOKED" width="200" />
</p>

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)

## Pre-requisites

- Python >= 3.12
- Git >= 2.51.0
- gitleaks >= 8.28.0

## Usage

`hooked` automatically configures your local environment to use the global git
hooks and executes them based on a ruleset. At the moment, these rulesets support
`pre-commit` and `gitleaks`. An example ruleset can be
found [here](https://github.com/conmob-devsecops/hooked-ruleset-tsi).

## Installation

Install this package directly from this repository using pip:

```bash
pip install git+https://github.com/conmob-devsecops/hooked.git@feature/initial-setup
```

_Note:_ Use `@<branch-name>` to install a specific branch, or
`@<tag-name>` to install a specific release.

After `hooked` is available on your `PATH`, you can run:

```bash
hooked enable --ruleset https://github.com/conmob-devsecops/hooked-ruleset-tsi
```

Rulesets are stored locally. By default, the `main` branch is used, but you
can specify a different branch using the `--branch` option.

## Keeping up to date

To update the ruleset repository, run:

```bash
hooked update
```

To update `hooked` itself, run:

```bash
hooked self-upgrade
```

Or you can the built-in update command, see `--help` for more information:

```bash
hooked --help
```

## One time skip

To skip the execution of `hooked` for a single commit, use the `HOOKED_SKIP`, e.g.:

```bash
HOOKED_SKIP=1 git commit -m "My commit message"
```

## Disable hooked

To disable `hooked` and remove the global git hooks, run:

```bash
hooked disable
```

This will disable the hooked ruleset. The current local ruleset will remain on
your device and can be re-enabled at any time using the `hooked enable` command.

If you want to remove the local ruleset as well, use the `--prune` option:

```bash
hooked disable --prune
```

After this, re-enabling `hooked` will require specifying a ruleset again.

## Uninstall

To uninstall `hooked`, run:

```bash
hooked disable --prune
pip uninstall hooked
```

## Configuration

### Environment variables

| Variable                    | Description                                                   |
|-----------------------------|---------------------------------------------------------------|
| `HOOKED_SKIP_UPGRADE_CHECK` | If set to any value disables the automatic upgrade check.     |
| `HOOKED_LOG_LEVEL`          | Sets the logging level.                                       |
| `HOOKED_SKIP`               | If set to any value. skips the execution of pre-commit hooks. |

## Development

To install the development dependencies, create a virtual environment and
activate it:

```bash
uv sync --dev
```

This will create a `.venv` directory with the virtual environment. Use this as
your Python interpreter in your IDE, or activate it manually, depending on
your setup.

You can use `uv` to run commands in the virtual environment:

```bash
uv run python --version
Python 3.14.0
```

`uv` can also be used to interact with your development setup of `hooked`:

```bash
uv run hooked --help
```

### Running tests

To run the tests, use `pytest`:

```bash
uv run pytest --cov=src/hooked
```
