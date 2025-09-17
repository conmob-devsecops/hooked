from .cmd_util import run_cmd
import os


def get_config_git_repo(base_dir: str, repo: str, branch: str):
    """Clones the configuration Git repository."""
    config_dir = os.path.join(base_dir, "config")
    cmd_git_clone = ["git", "clone", repo, config_dir]
    run_cmd(cmd_git_clone)

    cmd_git_checkout = ["git", "-C", config_dir, "checkout", branch]
    run_cmd(cmd_git_checkout)


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
