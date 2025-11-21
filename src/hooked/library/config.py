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

from hooked.library import files, git
from hooked.library.logger import logger


def install_config(repo: str, branch: str):
    """Clones the configuration Git repository."""
    config_dir = files.get_config_dir()

    if os.path.isdir(config_dir):
        logger.info("Existing config detected. Replacing it ...")
        files.remove_config_dir()

    git.git_clone_repo(repo=repo, dest=config_dir)
    git.git_checkout_branch(repo=config_dir, branch=branch)

    logger.debug("Config installed successfully.")


def update_config(force: bool = False):
    """Updates the configuration Git repository."""
    logger.info("Updating config ...")
    config_dir = files.get_config_dir()

    if not os.path.isdir(config_dir):
        logger.error(
            "Config does not exist. Install a rule set first via `hooked install`."
        )
        raise FileNotFoundError()

    if not git.is_git_repo(config_dir):
        logger.error("Config is not updateable (not a git repository).")
        raise RuntimeError()

    git.git_fetch_origin(repo=config_dir)

    if force:
        git.git_reset_hard_to_origin(repo=config_dir)

    else:
        git.git_try_merge(repo=config_dir)

    logger.info("Config updated successfully.")
