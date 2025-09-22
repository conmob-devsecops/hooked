import os
import platform
import shutil
from importlib.resources import files, as_file
from hooked.library.logger import logger


def get_base_dir() -> str:
    """Get the base directory for hooked configuration."""
    if platform.system() == "Windows":
        return os.path.join(os.path.expanduser("~"), ".config", "hooked")
    else:
        return os.path.join(os.path.expanduser("~"), ".config", "hooked")


def get_hooks_dir() -> str:
    """Get the hooks directory for hooked configuration."""
    base_dir = get_base_dir()
    return os.path.join(base_dir, "git_hooks")


def get_config_dir() -> str:
    """Get the config directory for hooked configuration."""
    base_dir = get_base_dir()
    return os.path.join(base_dir, "config")


def get_template_dir() -> str:
    """Get the git template directory for hooked configuration."""
    base_dir = get_base_dir()
    return os.path.join(base_dir, "git_template")


def _create_base_dir():
    """Create the base directory if it doesn't exist."""
    base_dir = get_base_dir()
    os.makedirs(base_dir, exist_ok=True)
    logger.debug(f"Base directory created at {base_dir}")


def _create_hooks_dir():
    """Create the git_hooks directory if it doesn't exist."""
    base_dir = get_base_dir()
    hooks_dir = os.path.join(base_dir, "git_hooks")
    os.makedirs(hooks_dir, exist_ok=True)
    logger.debug(f"Hooks directory created at {hooks_dir}")
    return hooks_dir


def _create_git_template_dir():
    """Create the git_template directory if it doesn't exist."""
    base_dir = get_base_dir()
    git_template_dir = os.path.join(base_dir, "git_template")
    os.makedirs(git_template_dir, exist_ok=True)
    logger.debug(f"Git templates directory created at {git_template_dir}")
    return git_template_dir


def _copy_git_hooks(git_hooks_src_path: str, git_hooks_dst_dir: str):
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
    logger.debug("Git hooks copied.")


def copy_hooked_files():
    _create_base_dir()
    _create_git_template_dir()
    _create_hooks_dir()
    _copy_git_hooks("hooked.data.git_hooks", get_hooks_dir())
    logger.debug("Git global hooks copied.")
    _copy_git_hooks("hooked.data.git_template", get_template_dir())
    logger.debug("Git template copied.")


def remove_base_dir(base_dir: str):
    """Remove the base directory and all its contents."""
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
