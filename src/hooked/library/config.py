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
import shutil

from hooked.library.cmd_util import CommandError, run_cmd
from hooked.library.logger import logger


def install_config(base_dir: str, repo: str, branch: str):
    """Clones the configuration Git repository."""
    config_dir = os.path.join(base_dir, "config")

    if os.path.isdir(config_dir):
        logger.info("Existing config detected. Replacing it ...")
        shutil.rmtree(config_dir)

    try:
        run_cmd(["git", "clone", repo, config_dir])
    except CommandError as e:
        logger.warning(f"Git clone failed: {e.result.stderr}")
        raise

    try:
        run_cmd(["git", "-C", config_dir, "checkout", branch])
    except CommandError as e:
        logger.warning(f"Git checkout failed: {e.result.stderr}")
        raise

    logger.debug("Config installed successfully.")


def update_config(base_dir: str, force: bool = False):
    """Updates the configuration Git repository."""
    logger.info("Updating config ...")
    config_dir = os.path.join(base_dir, "config")
    git_dir = os.path.join(config_dir, ".git")

    if not os.path.isdir(config_dir):
        logger.error("Config does not exist. Install a rule set first.")
        raise

    if not os.path.isdir(git_dir):
        logger.error("Config is not updateable (not a git repository).")
        raise

    try:
        run_cmd(
            [
                "git",
                "-C",
                config_dir,
                "fetch",
                "--prune",
                "--tags",
                "origin",
            ]
        )
    except CommandError as e:
        logger.error(f"Git fetch failed: {e.result.stderr}")
        raise

    if force:
        try:
            run_cmd(["git", "-C", config_dir, "reset", "--hard", "origin/HEAD"])
        except CommandError as e:
            logger.error(f"Git reset failed: {e.result.stderr}")
            raise
    else:
        try:
            run_cmd(
                [
                    "git",
                    "-C",
                    config_dir,
                    "-c",
                    "rebase.autoStash=true",
                    "pull",
                    "--no-rebase",
                    "--no-edit",
                    "--strategy-option",
                    "ours",
                ]
            )
        except CommandError as e:
            logger.error(f"Git merge failed: {e.result.stderr}")
            raise

    logger.info("Config updated successfully.")
