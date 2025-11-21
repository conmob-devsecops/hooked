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

from hooked.library.cmd import CommandError, run_cmd
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
        run_cmd(["git", "config", "--global", "init.templatedir", template_dir])
    except CommandError as e:
        logger.error(f"git config failed: {e.result.stderr}")
        raise


def git_unset_template_dir():
    """Unset the global git template directory."""
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


def git_clone_repo(repo: str, dest: str) -> None:
    """Clones a git repository into a destination directory"""
    try:
        run_cmd(["git", "clone", repo, dest])
    except CommandError as e:
        logger.error(f"Git clone failed: {e.result.stderr}")
        raise


def git_checkout_branch(repo: str, branch: str) -> None:
    """Checks out a branch in a given git repository"""
    try:
        run_cmd(["git", "-C", repo, "checkout", branch])
    except CommandError as e:
        logger.error(f"Git checkout failed: {e.result.stderr}")
        raise


def git_fetch_origin(repo: str) -> None:
    """Fetches the latest commits from origin for given git repository"""
    try:
        run_cmd(
            [
                "git",
                "-C",
                repo,
                "fetch",
                "--prune",
                "--tags",
                "origin",
            ]
        )
    except CommandError as e:
        logger.error(f"Git fetch failed: {e.result.stderr}")
        raise


def git_reset_hard_to_origin(repo: str) -> None:
    """Resets a given repo hard to origin/HEAD"""
    try:
        run_cmd(["git", "-C", repo, "reset", "--hard", "origin/HEAD"])
    except CommandError as e:
        logger.error(f"Git reset failed: {e.result.stderr}")
        raise


def git_try_merge(repo: str) -> None:
    """Try to merge merge a given repository with the latest fetched changes"""
    try:
        run_cmd(
            [
                "git",
                "-C",
                repo,
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


def is_git_repo(dir: str) -> bool:
    """Returns true if the directory is a git repository"""
    try:
        result = run_cmd(["git", "rev-parse", "--is-inside-work-tree"], cwd=dir)
        return "true" in str(result.stdout)
    except CommandError as e:
        if "not a git repository" in str(e.result.stderr):
            return False
        raise


def git_has_staged_files(repo: str) -> bool:
    """Returns true if there are staged files in the git repository"""
    try:
        result = run_cmd(
            ["git", "diff", "--cached", "--name-only", "--diff-filter", "ACM"], cwd=repo
        )
        return str(result.stdout) != ""
    except CommandError as e:
        logger.error(f"Git diff failed: {e.result.stderr}")
        raise


def git_has_hook_installed(repo: str, hook: str) -> bool:
    """Returns true if a certain hook is installed in the repository"""
    hook_path = os.path.join(repo, ".git", "hooks", hook)

    return os.path.isfile(hook_path) and os.access(hook_path, os.X_OK)


def git_run_hook(repo: str, hook: str, env: dict[str, str] | None = None) -> None:
    try:
        hook_path = os.path.join(repo, ".git", "hooks", hook)
        run_cmd([hook_path], env=env, cwd=repo)
    except CommandError as e:
        logger.error(f"Error while running git hook: {e}")
        raise
