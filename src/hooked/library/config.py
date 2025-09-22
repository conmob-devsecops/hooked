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
