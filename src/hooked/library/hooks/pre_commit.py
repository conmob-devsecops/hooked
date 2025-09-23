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

import os
from datetime import datetime, timedelta
from pathlib import Path

from hooked import __upgrade_interval_seconds__
from hooked.library.cmd_util import run_cmd, CommandError, run_stream
from hooked.library.config import update_config_git_repo
from hooked.library.files import (
    create_hooks_dir,
    create_git_template_dir,
    copy_git_hooks,
)
from hooked.library.files import get_base_dir
from hooked.library.logger import logger
from hooked.library.upgrade import (
    get_last_upgrade_timestamp,
    self_upgrade,
    set_last_upgrade_timestamp,
)

from hooked.library.pre_commit_util import is_hook_error


def _pre_commit_version():
    version = run_cmd(["pre-commit", "--version"]).stdout
    logger.debug(f"running {version}")


def run_pre_commit_hook(cwd: str = None) -> int:
    """
    Serves as entrypoint for running pre-commit hooks on staged files in a git repository.

    Args:
        cwd (str): The current working directory where the git repository is located.

    Returns:
        int: Exit code indicating success (0) or failure (1) of the pre-commit hooks.
    """
    if not cwd:
        raise RuntimeError("Missing required cwd argument")

    try:
        _pre_commit_version()
    except CommandError as exc:
        raise RuntimeError("pre-commit is not installed or not found in PATH") from exc

    base_dir = get_base_dir()
    config_dir = os.path.join(base_dir, "config")

    last_run = get_last_upgrade_timestamp()
    logger.debug(f"Last pre-commit run at {last_run}")

    now = datetime.now()
    delta = timedelta(seconds=__upgrade_interval_seconds__)

    skip_check = os.getenv("HOOKED_SKIP_UPGRADE_CHECK", "false").lower() in (
        "1",
        "true",
        "yes",
    )

    if (last_run and now - last_run < delta) and not skip_check:
        logger.debug(
            "Pre-commit upgrade skipped due to upgrade interval or skipped due environment setting."
        )
    else:
        logger.always("Running hooked self-upgrade...")
        self_upgrade()

        logger.debug("Updating hooked rules...")
        update_config_git_repo(base_dir)

        logger.debug("Installing latest version of hooked git hooks...")
        hooks_dir = create_hooks_dir(base_dir)
        templates_dir = create_git_template_dir(base_dir)
        copy_git_hooks("hooked.data.git_hook_templates", templates_dir)
        copy_git_hooks("hooked.data.git_hooks", hooks_dir)

        logger.debug("Running pre-commit autoupdate...")
        run_cmd(["pre-commit", "autoupdate"], cwd=config_dir)

        set_last_upgrade_timestamp()

    cwd_path = Path(cwd[0]).resolve()
    if not cwd_path.exists() or not cwd_path.is_dir():
        raise RuntimeError(f"Provided path {cwd} does not exist or is not a directory")

    logger.always("Starting to work in the target repository %s...", cwd_path)

    staged_files = run_cmd(
        ["git", "diff", "--cached", "--name-only", "--diff-filter", "ACM"],
        cwd=str(cwd_path),
    ).stdout
    if not staged_files:
        logger.info("No staged files to check.")
        return 0

    logger.debug(f"Staged files: {staged_files.replace('\n', ', ')}")
    logger.debug("Running pre-commit hooks...")
    try:
        pre_commit_config = os.path.join(config_dir, ".pre-commit-config.yaml")

        _env = os.environ.copy()
        _env["GITLEAKS_CONFIG"] = os.path.join(config_dir, ".gitleaks.toml")
        _env["PRE_COMMIT_COLOR"] = "always"

        run_stream(
            [
                "pre-commit",
                "run",
                "--config",
                pre_commit_config,
            ],
            env=_env,
            cwd=str(cwd_path),
        )
    except CommandError as exc:
        if not is_hook_error(exc):
            raise

        logger.warning("Pre-commit hooks failed. Please fix the issues and try again.")
        return 1

    local_pre_commit_file = cwd_path.joinpath(".pre-commit-config.yaml")
    if not local_pre_commit_file.is_file():
        logger.debug("No .pre-commit-config.yaml found in repository.")
        return 0

    logger.always(".pre-commit-config.yaml found. Running local pre-commit hooks...")

    _env = os.environ.copy()
    _env["PRE_COMMIT_COLOR"] = "always"

    try:
        run_stream(
            [
                "pre-commit",
                "run",
                "--config",
                str(local_pre_commit_file),
            ],
            env=_env,
            cwd=str(cwd_path),
        )
    except CommandError as exc:
        if not is_hook_error(exc):
            raise

        logger.warning("Pre-commit hooks failed. Please fix the issues and try again.")
        return 1

    logger.always("pre-commit hook ran successfully.")

    return 0
