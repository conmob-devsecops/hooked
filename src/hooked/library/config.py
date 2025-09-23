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

from .cmd_util import run_cmd, CommandError
import os
from .logger import logger


def get_config_git_repo(base_dir: str, repo: str, branch: str) -> int:
    """Clones the configuration Git repository."""
    config_dir = os.path.join(base_dir, "config")
    cmd_git_clone = ["git", "clone", repo, config_dir]
    try:
        run_cmd(cmd_git_clone)
    except CommandError as e:
        if getattr(e, "result", None) and getattr(e.result, "returncode", None) == 128:
            logger.warning("Git clone failed, repository already exists.")
            return 0
        raise

    cmd_git_checkout = ["git", "-C", config_dir, "checkout", branch]
    logger.debug("Pre-commit config installed.")
    return run_cmd(cmd_git_checkout).returncode


def update_config_git_repo(base_dir: str, force: bool = False):
    """Updates the configuration Git repository."""
    config_dir = os.path.join(base_dir, "config")

    if force:
        cmd_git_fetch = [
            "git",
            "-C",
            config_dir,
            "fetch",
            "--prune",
            "--tags",
            "origin",
        ]
        run_cmd(cmd_git_fetch)

        cmd_git_reset = ["git", "-C", config_dir, "reset", "--hard", "origin/HEAD"]
        run_cmd(cmd_git_reset)
    else:
        cmd_git_fetch = ["git", "-C", config_dir, "fetch", "--prune", "origin"]
        run_cmd(cmd_git_fetch)

        cmd_git_merge = [
            "git",
            "-C",
            config_dir,
            "-c",
            "ebase.autoStash=true",
            "ull",
            "--no-rebase",
            "--no-edit",
            "--strategy-option",
            "ours",
        ]
        run_cmd(cmd_git_merge)
