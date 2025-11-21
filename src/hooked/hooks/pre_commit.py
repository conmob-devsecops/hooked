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

import os
from datetime import datetime, timedelta
from pathlib import Path

from hooked.__meta__ import __upgrade_interval_seconds__
from hooked.library import config, files, git, pre_commit, upgrade
from hooked.library.cmd import CommandError
from hooked.library.logger import logger
from hooked.library.utils import is_hook_error


def run(cwd: str = "") -> None:
    cwd = _normalize_cwd(cwd=cwd)

    if _check_autoupdate():
        _do_autoupdate()

    if not _flag_is_set("HOOKED_SKIP"):
        _run_internal_precommit(cwd=cwd)

    if pre_commit.is_pre_commit_available(
        repo=cwd
    ) and not pre_commit.is_pre_commit_installed(repo=cwd):
        logger.info("Uninstalled pre-commit detected, installing ...")
        pre_commit.pre_commit_install(repo=cwd)

    if git.git_has_hook_installed(repo=cwd, hook="pre-commit"):
        git.git_run_hook(repo=cwd, hook="pre-commit")


def _flag_is_set(env_var: str) -> bool:
    return os.getenv(env_var, "false").lower() in ("1", "true", "yes")


def _normalize_cwd(cwd: str) -> str:
    if not cwd:
        raise RuntimeError("Missing required cwd argument")

    cwd = str(Path(cwd[0]).resolve())
    if not os.path.exists(cwd):
        raise RuntimeError(f"Provided path {cwd} does not exist")
    if not os.path.isdir(cwd):
        raise RuntimeError(f"Provided path {cwd} is not a directory")

    return cwd


def _check_autoupdate() -> bool:
    last_run = upgrade.get_last_upgrade_timestamp()
    logger.debug(f"Last pre-commit run at {last_run}")

    now = datetime.now()
    delta = timedelta(seconds=__upgrade_interval_seconds__)

    if _flag_is_set("HOOKED_SKIP"):
        logger.debug("Pre-commit upgrade skipped due environment setting.")
        return False

    if last_run and now - last_run < delta:
        logger.debug("Pre-commit upgrade skipped due to upgrade interval.")
        return False

    return True


def _run_internal_precommit(cwd: str) -> None:
    logger.debug("Running internal pre-commit hooks...")
    config_dir = files.get_config_dir()
    try:
        pre_commit_config = os.path.join(config_dir, ".pre-commit-config.yaml")

        env = os.environ.copy()
        env["GITLEAKS_CONFIG"] = os.path.join(config_dir, ".gitleaks.toml")

        pre_commit.pre_commit_run(config=pre_commit_config, env=env, cwd=cwd)
    except CommandError as e:
        if not is_hook_error(e):
            raise
        logger.warning("Pre-commit hooks failed. Please fix the issues and try again.")


def _do_autoupdate() -> None:
    last_run = upgrade.get_last_upgrade_timestamp()
    logger.debug(f"Last pre-commit run at {last_run}")

    logger.info("Running hooked self-upgrade...")
    upgrade.self_upgrade()

    logger.debug("Updating hooked rules...")
    config.update_config()

    logger.debug("Installing latest version of hooked git hooks...")
    files.copy_hooked_files()

    logger.debug("Running pre-commit autoupdate...")
    config_dir = files.get_config_dir()
    pre_commit.pre_commit_autoupdate(repo=config_dir)

    upgrade.set_last_upgrade_timestamp()
