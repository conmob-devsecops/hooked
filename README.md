<p align=center>
  <img src="./docs/assets/banner.jpg" alt="HOOKED" style="margin:0px" />
</p>

[![GitHub Tag](https://img.shields.io/github/v/tag/conmob-devsecops/hooked?label=Version&color=e20074)](https://github.com/conmob-devsecops/hooked/releases)
![GitHub License](https://img.shields.io/github/license/conmob-devsecops/hooked)
![Python](https://img.shields.io/badge/Python-%E2%89%A5%203.12-%233776AB?logo=Python&logoColor=%23ffffff)
![Git](https://img.shields.io/badge/Git-%E2%89%A5%202.9.0-%23F05032?logo=Git&logoColor=%23ffffff)
[![pre-commit](https://img.shields.io/badge/pre--commit-%E2%89%A5%204.0.0-%23FAB040?logo=pre-commit&logoColor=ffffff)](https://pre-commit.com/)

## Hooked

Hooked is a tool to automate of the use of pre-commit hooks in your local
repositories. It configures your local environment by inserting global hooks
and templates into your git workflow.

At the moment, only [pre-commit](https://pre-commit.com/) is supported. Other
frameworks may be added in the future.

## 🌱 Installation

**Prerequisites**

- **Python** ≥ 3.12 [Website](https://www.python.org/) | [Github](https://github.com/python/)
- **Git** ≥ 2.9.0 [Website](https://git-scm.com/) | [Git](https://git.kernel.org/pub/scm/git/git.git)
- **Gitleaks** ≥ 8.28.0 [Website](https://gitleaks.io/) | [Github](https://github.com/gitleaks/gitleaks)
- **pre-commit** ≥ 4.0.0 [Website](https://pre-commit.com/) | [Githu
  b](https://github.com/pre-commit/pre-commit)

You may check the installed versions of the dependencies on your system with
this script.

```bash
curl -fsSL https://raw.githubusercontent.com/conmob-devsecops/hooked/refs/heads/main/check_prerequisites.sh | bash
```

Hooked itself will be installed via `pip`.

```bash
pip install git+https://github.com/conmob-devsecops/hooked.git@main
```

⚠️ Some managed python environments (e.g., homebrew) don't allow you to install
hooked via pip directly. Please read [installation manual](./docs/install.md)
for more details.

By now hooked should be available on your shell. You may check the version of
hooked.

```bash
$ hooked version
Hooked version: 0.1.0
```

Next, we need a rule set installed, for hooked to work. An example rule set can
be found at [hooked-ruleset-tsi](https://github.com/conmob-devsecops/hooked-ruleset-tsi).
Rule sets are stored locally. By default, the `main` branch is used, but you
can specify a different branch using the `--branch` option.

```bash
hooked install https://github.com/conmob-devsecops/hooked-ruleset-tsi.git
```

Congratulations 🎉 You now have hooked installed on your system!

## Usage

```bash
# update the installed rule set
hooked update

# update hooked itself
hooked self-upgrade

# Get the hooked help
hooked --help

# skip the execution of hooked for a single commit
HOOKED_SKIP=1 git commit -m "my commit message"

# disable hooked
hooked disable

# enable hooked again
hooked enable

# disable hooked and remove local rule set
hooked disable --prune

# uninstall hooked
hooked disable --prune
pip uninstall hooked
```

**Environment variables**

| Variable                    | Description                                                   |
| --------------------------- | ------------------------------------------------------------- |
| `HOOKED_SKIP_UPGRADE_CHECK` | If set to any value disables the automatic upgrade check.     |
| `HOOKED_LOG_LEVEL`          | Sets the logging level.                                       |
| `HOOKED_SKIP`               | If set to any value. skips the execution of pre-commit hooks. |

## Development

To install the development dependencies, create a virtual environment and
activate it:

```bash
uv sync --dev
uv venv
source .venv/bin/activate
```

This will create a `.venv` directory with the virtual environment. Use this as
your Python interpreter in your IDE, or activate it manually, depending on
your setup.

To run the tests, use `pytest`:

```bash
uv run pytest --cov=src/hooked
```
