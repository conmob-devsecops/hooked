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

from hooked.library.cmd_util import CommandError, run_cmd
from hooked.library.logger import logger


def git_set_global_hook_path(hooks_dir: str):
    """Set the global git hooks path to the specified directory."""
    try:
        run_cmd(["git", "config", "--global", "core.hooksPath", hooks_dir])
    except CommandError as e:
        logger.error(f"Git config failed: {e.result.stderr}")
        raise


def git_unset_global_hook_path():
    """Unset the global git hooks path."""
    try:
        run_cmd(["git", "config", "--global", "--unset", "core.hooksPath"])
    except CommandError as e:
        if getattr(e, "result", None) and getattr(e.result, "returncode", None) == 5:
            logger.warning("Git global hooksPath not set, nothing to unset.")
            return
        raise


def git_set_template_dir(template_dir: str):
    """Set the global git template directory to the specified directory."""
    try:
        run_cmd(["git", "config", "--global", "init.templateDir", template_dir])
    except CommandError as e:
        logger.error(f"Git config failed: {e.result.stderr}")
        raise


def git_unset_template_dir():
    """Unset the global git template directory."""
    cmd = ["git", "config", "--global", "--unset", "init.templateDir"]
    try:
        run_cmd(["git", "config", "--global", "--unset", "init.templateDir"])
    except CommandError as e:
        if getattr(e, "result", None) and getattr(e.result, "returncode", None) == 5:
            logger.warning("Git global templateDir not set, nothing to unset.")
            return
        raise


def git_get_tags(url: str) -> list[tuple[str, str]]:
    """
    Get all tags from a remote git repository.

    Returns a list of tuples (tag, sha).
    """
    clean = url
    if clean.startswith("git+"):
        clean = clean[4:]

    stdout = run_cmd(["git", "ls-remote", "--tags", "--refs", clean]).stdout
    tags = []
    if stdout is None:
        return tags
    for line in stdout.splitlines():
        sha, ref = line.split("\t")
        if ref.startswith("refs/tags/"):
            tag = ref.split("/", 2)[2]
            tags.append((tag, sha))
    return tags


def git_get_last_branch_commit(url: str, branch: str) -> str | None:
    """
    Get the latest commit SHA for a given branch from a remote git repository.

    Returns the SHA as a string, or None if not found.
    """
    clean = url
    if clean.startswith("git+"):
        clean = clean[4:]
    stdout = run_cmd(["git", "ls-remote", "--heads", clean, branch]).stdout
    if stdout is None:
        return None
    for line in stdout.splitlines():
        sha, ref = line.split("\t")
        if ref == f"refs/heads/{branch}":
            return sha
    return None
