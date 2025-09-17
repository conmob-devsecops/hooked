from .cmd_util import run_cmd, CommandError

from .logger import logger


def git_set_global_hook_path(hooks_dir: str) -> int:
    """Set the global git hooks path to the specified directory."""
    cmd = ["git", "config", "--global", "core.hooksPath", hooks_dir]
    return run_cmd(cmd).returncode


def git_unset_global_hook_path() -> int:
    """Unset the global git hooks path."""
    cmd = ["git", "config", "--global", "--unset", "core.hooksPath"]
    try:
        return run_cmd(cmd).returncode
    except CommandError as e:
        if getattr(e, "result", None) and getattr(e.result, "returncode", None) == 5:
            logger.warning("Git global hooksPath not set, nothing to unset.")
            return 0
        raise


def git_set_template_dir(template_dir: str) -> int:
    """Set the global git template directory to the specified directory."""
    cmd = ["git", "config", "--global", "init.templateDir", template_dir]
    return run_cmd(cmd).returncode


def git_unset_template_dir() -> int:
    """Unset the global git template directory."""
    cmd = ["git", "config", "--global", "--unset", "init.templateDir"]
    try:
        return run_cmd(cmd).returncode
    except CommandError as e:
        if getattr(e, "result", None) and getattr(e.result, "returncode", None) == 5:
            logger.warning("Git global templateDir not set, nothing to unset.")
            return 0
        raise


def git_get_tags(url: str) -> list[tuple[str, str]]:
    """
    Get all tags from a remote git repository.

    Returns a list of tuples (tag, sha).
    """
    clean = url
    if clean.startswith("git+"):
        clean = clean[4:]

    out = run_cmd(["git", "ls-remote", "--tags", "--refs", clean]).stdout
    tags = []
    for line in out.splitlines():
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
    out = run_cmd(["git", "ls-remote", "--heads", clean, branch]).stdout
    for line in out.splitlines():
        sha, ref = line.split("\t")
        if ref == f"refs/heads/{branch}":
            return sha
    return None
