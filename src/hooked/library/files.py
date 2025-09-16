import os
import platform
import shutil
from importlib.resources import files, as_file


def get_base_dir() -> str:
    """Get the base directory for hooked configuration."""
    if platform.system() == "Windows":
        return os.path.join(os.path.expanduser("~"), "AppData", "Local", "hooked")
    else:
        return os.path.join(os.path.expanduser("~"), ".config", "hooked")


def create_base_dir(base_dir) -> str:
    """Create the base directory if it doesn't exist."""
    os.makedirs(base_dir, exist_ok=True)
    return base_dir


def create_hooks_dir(base_dir: str) -> str:
    """Create the git_hooks directory if it doesn't exist."""
    hooks_dir = os.path.join(base_dir, "git_hooks")
    os.makedirs(hooks_dir, exist_ok=True)
    return hooks_dir


def create_git_template_dir(base_dir: str) -> str:
    """Create the git_template directory if it doesn't exist."""
    git_template_dir = os.path.join(base_dir, "git_template")
    os.makedirs(git_template_dir, exist_ok=True)
    return git_template_dir


def copy_git_hooks(git_hooks_src_path: str, git_hooks_dst_dir: str):
    """Copy git hook scripts to the git_hooks directory."""
    git_hooks_src_dir = files(git_hooks_src_path)
    with as_file(git_hooks_src_dir) as git_hooks_src:
        for root, dirs, _files in os.walk(git_hooks_src):
            rel_path = os.path.relpath(root, git_hooks_src)
            dest_dir = os.path.join(git_hooks_dst_dir, rel_path)
            os.makedirs(dest_dir, exist_ok=True)
            for file in _files:
                src_file_path = os.path.join(root, file)
                dst_file_path = os.path.join(dest_dir, file)
                with open(src_file_path) as src_file:
                    with open(dst_file_path, "w") as dst_file:
                        dst_file.write(src_file.read())
                os.chmod(dst_file_path, 0o755)


def remove_base_dir(base_dir: str):
    """Remove the base directory and all its contents."""
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
