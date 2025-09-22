from hooked.library.cmd_util import run_cmd, CommandError
from hooked.library.files import (
    get_base_dir,
    get_hooks_dir,
    get_template_dir,
    copy_hooked_files,
    remove_base_dir,
)
from hooked.library.git import (
    git_set_global_hook_path,
    git_unset_global_hook_path,
    git_set_template_dir,
    git_unset_template_dir,
)
from hooked.library.config import get_config_git_repo
from hooked.library.logger import logger

from packaging.version import Version, InvalidVersion


def _get_gitleaks_version() -> str:
    try:
        return run_cmd(["gitleaks", "--version"]).stdout
    except CommandError:
        raise


def _check_gitleaks():
    try:
        version_raw = _get_gitleaks_version()
        version_split = version_raw.split()
        try:
            version = Version(version_split[2])
            logger.info(f"gitleaks version {version} found.")
        except (InvalidVersion, IndexError):
            raise RuntimeError(f"Unable to parse gitleaks version from: {version_raw}")
    except CommandError as e:
        logger.error("gitleaks is not installed or not found in PATH.")
        raise RuntimeError(
            "gitleaks is required but not installed or not found in PATH."
        ) from e


def _get_git_version() -> str:
    try:
        return run_cmd(["git", "--version"]).stdout
    except CommandError:
        raise


def _check_git():
    try:
        version_raw = _get_git_version()
        version_split = version_raw.split()
        try:
            version = Version(version_split[2])
            logger.info(f"git version {version} found.")
        except (InvalidVersion, IndexError):
            raise RuntimeError(f"Unable to parse git version from: {version_raw}")
    except CommandError as e:
        logger.error("git is not installed or not found in PATH.")
        raise RuntimeError(
            "git is required but not installed or not found in PATH."
        ) from e


def check_pre_requisites() -> int:
    try:
        _check_gitleaks()
    except RuntimeError as e:
        logger.critical(
            "There was a problem with determining if `gitleaks` is installed: %s.", e
        )
        logger.into(
            "Please install `gitleaks` and ensure it is available in your PATH."
        )
        logger.info(
            "For installation instructions, visit: https://github.com/gitleaks/gitleaks"
        )
        return 1

    try:
        _check_git()
    except RuntimeError as e:
        logger.critical(
            "There was a problem with determining if `git` is installed: %s.", e
        )
        logger.into("Please install `git` and ensure it is available in your PATH.")
        logger.info("Download `git` from: https://git-scm.com/downloads")
        logger.info(
            "For installation instructions, visit: https://git-scm.com/book/en/v2/Getting-Started-Installing-Git"
        )
        return 1

    logger.info("All pre-requisites are met.")
    return 0


def install(rules: str, branch: str) -> int:
    logger.debug("Installing hooked...")
    copy_hooked_files()

    get_config_git_repo(get_base_dir(), rules, branch)

    git_set_global_hook_path(get_hooks_dir())
    logger.debug("Set Git global hooks path.")

    git_set_template_dir(get_template_dir())
    logger.debug("Set Git global template directory.")

    return 0


def uninstall() -> int:
    logger.debug("Uninstalling hooked...")

    remove_base_dir(get_base_dir())
    logger.debug("Config directory removed.")
    git_unset_global_hook_path()
    logger.debug("Reset Git global hooks path.")
    git_unset_template_dir()
    logger.debug("Reset Git global template directory.")

    logger.debug("hooked uninstalled.")

    return 0
