#  Copyright 2025 T-Systems International GmbH
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are met:
#
#  1. Redistributions of source code must retain the above copyright notice, this
#     list of conditions and the following disclaimer.
#
#  2. Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#
#  3. Neither the name of the copyright holder nor the names of its
#     contributors may be used to endorse or promote products derived from
#     this software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#  AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#  IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#  DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
#  FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
#  DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#  SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
#  CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#  OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from __future__ import annotations

import re

from packaging.version import InvalidVersion, Version

from hooked.__meta__ import (
    __min_git_version__,
    __min_gitleaks_version__,
    __min_precommit_version__,
)
from hooked.library.cmd import CommandError, run_cmd
from hooked.library.config import install_config
from hooked.library.files import (
    copy_hooked_files,
    get_base_dir,
    get_hooks_dir,
    get_template_dir,
    remove_base_dir,
)
from hooked.library.git import (
    git_set_global_hook_path,
    git_set_template_dir,
    git_unset_global_hook_path,
    git_unset_template_dir,
)
from hooked.library.logger import logger


def _parse_version(v: str) -> Version:
    try:
        return Version(v)
    except InvalidVersion:
        m = re.search(r"(\d+\.\d+\.\d+)", v)
        if m is None:
            return Version("0.0.0")
        return Version(m.group(0))


def _get_gitleaks_version() -> str:
    try:
        return str(run_cmd(["gitleaks", "--version"]).stdout)
    except CommandError:
        raise


def _check_gitleaks():
    try:
        version_raw = _get_gitleaks_version()
        version_split = version_raw.split()
        try:
            version = _parse_version(version_split[2])
            logger.info(f"gitleaks version {version} found.")
        except (InvalidVersion, IndexError):
            raise RuntimeError(f"Unable to parse gitleaks version from: {version_raw}")
        if version < __min_gitleaks_version__:
            raise RuntimeError(
                f"gitleaks must have minimum version of {__min_gitleaks_version__}"
            )
    except CommandError as e:
        logger.error("gitleaks is not installed or not found in PATH.")
        logger.info(
            "Please install `gitleaks` and ensure it is available in your PATH."
        )
        logger.info(
            "For installation instructions, visit: https://github.com/gitleaks/gitleaks"
        )
        raise RuntimeError(
            "gitleaks is required but not installed or not found in PATH."
        ) from e


def _get_git_version() -> str:
    try:
        return str(run_cmd(["git", "--version"]).stdout)
    except CommandError:
        raise


def _check_git():
    try:
        version_raw = _get_git_version()
        version_split = version_raw.split()
        try:
            version = _parse_version(version_split[2])
            logger.info(f"git version {version} found.")
        except (InvalidVersion, IndexError):
            raise RuntimeError(f"Unable to parse git version from: {version_raw}")
        if version < __min_git_version__:
            raise RuntimeError(
                f"git must have minimum version of {__min_git_version__}"
            )
    except CommandError as e:
        logger.error("git is not installed or not found in PATH.")
        logger.info("Please install `git` and ensure it is available in your PATH.")
        logger.info("Download `git` from: https://git-scm.com/downloads")
        logger.info(
            "For installation instructions, visit: https://git-scm.com/book/en/v2/Getting-Started-Installing-Git"
        )
        raise RuntimeError(
            "git is required but not installed or not found in PATH."
        ) from e


def _get_precommit_version() -> str:
    try:
        return str(run_cmd(["pre-commit", "--version"]).stdout)
    except CommandError:
        raise


def _check_precommit():
    try:
        version_raw = _get_precommit_version()
        version_split = version_raw.split()
        try:
            version = Version(version_split[1])
            logger.info(f"pre-commit version {version} found.")
        except (InvalidVersion, IndexError):
            raise RuntimeError(
                f"Unable to parse pre-commit version from: {version_raw}"
            )
        if version < __min_precommit_version__:
            raise RuntimeError(
                f"pre-commit must have minimum version of {__min_precommit_version__}"
            )
    except CommandError as e:
        logger.error("pre-commit is not installed or not found in PATH.")
        logger.info(
            "Please install `pre-commit` and ensure it is available in your PATH."
        )
        logger.info(
            "For installation instructions, visit: https://pre-commit.com/#install"
        )
        raise RuntimeError(
            "pre-commit is required but not installed or not found in PATH."
        ) from e


def check_pre_requisites():
    try:
        _check_gitleaks()
        _check_git()
        _check_precommit()
    except RuntimeError as e:
        logger.critical(e)
        raise

    logger.info("All pre-requisites are met.")


def disable(prune: bool = False):
    logger.info("Disabling hooked...")

    git_unset_global_hook_path()
    logger.debug("Git global hooks removed")

    git_unset_template_dir()
    logger.debug("Git global template directory removed")

    if prune:
        remove_base_dir(get_base_dir())
        logger.info("Config directory removed.")

    logger.info("hooked successfully disabled.")


def enable():
    logger.info("Enabling hooked ...")

    git_set_global_hook_path(get_hooks_dir())
    logger.debug("Git global hooks installed")

    git_set_template_dir(get_template_dir())
    logger.debug("Git global template directory installed")
    logger.info("hooked successfully enabled.")


def install(rules: str, branch: str):
    logger.info("Installing hooked rules ...")
    copy_hooked_files()
    install_config(repo=rules, branch=branch)
    enable()
