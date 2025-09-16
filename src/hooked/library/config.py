import os


def get_config_git_repo(base_dir: str, repo: str, branch: str):
    """Clones the configuration Git repository."""
    config_dir = os.path.join(base_dir, "config")

    os.system(f"git clone {repo} {config_dir}")
    os.system(f"git -C {config_dir} checkout {branch}")


def update_config_git_repo(base_dir: str, force: bool = False):
    """Updates the configuration Git repository."""
    config_dir = os.path.join(base_dir, "config")

    if force:
        os.system(f"git -C {config_dir} fetch --prune --tags origin")
        os.system(f"git -C {config_dir} reset --hard")
    else:
        os.system(f"git -C {config_dir} fetch --prune origin")
        os.system(
            f"git -C {config_dir} -c rebase.autoStash=true pull --no-rebase --no-edit --strategy-option ours"
        )
