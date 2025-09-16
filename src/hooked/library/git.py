import subprocess


def git_set_global_hook_path(hooks_dir: str) -> int:
    """Set the global git hooks path to the specified directory."""
    cmd = f"git config --global core.hooksPath {hooks_dir}"
    return subprocess.call(cmd.split())


def git_unset_global_hook_path() -> int:
    """Unset the global git hooks path."""
    cmd = "git config --unset core.hooksPath"
    return subprocess.call(cmd.split())


def git_set_template_dir(template_dir: str) -> int:
    """Set the global git template directory to the specified directory."""
    cmd = f"git config --global init.templateDir {template_dir}"
    return subprocess.call(cmd.split())


def git_unset_template_dir() -> int:
    """Unset the global git template directory."""
    cmd = "git config --global --unset init.templateDir"
    return subprocess.call(cmd.split())


def git_get_tags(url: str) -> list[tuple[str, str]]:
    """
    Get all tags from a remote git repository.

    Returns a list of tuples (tag, sha).
    """
    clean = url
    if clean.startswith("git+"):
        clean = clean[4:]
    out = subprocess.check_output(
        ["git", "ls-remote", "--tags", "--refs", clean], text=True
    )
    tags = []
    for line in out.strip().splitlines():
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
    out = subprocess.check_output(
        ["git", "ls-remote", "--heads", clean, branch], text=True
    )
    for line in out.strip().splitlines():
        sha, ref = line.split("\t")
        if ref == f"refs/heads/{branch}":
            return sha
    return None
