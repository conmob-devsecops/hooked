import os
from datetime import datetime, timedelta
from pathlib import Path

from hooked import __upgrade_interval_seconds__
from hooked.library.cmd_util import run_cmd, CommandError, run_stream
from hooked.library.config import update_config_git_repo
from hooked.library.files import (
    create_hooks_dir,
    create_git_template_dir,
    copy_git_hooks,
)
from hooked.library.files import get_base_dir
from hooked.library.logger import logger
from hooked.library.upgrade import (
    get_last_upgrade_timestamp,
    self_upgrade,
    set_last_upgrade_timestamp,
)


def _pre_commit_version():
    version = run_cmd(["pre-commit", "--version"]).stdout.strip()
    logger.debug(f"running {version}")


def run_pre_commit_hook(cwd: str = None) -> int:
    if not cwd:
        raise RuntimeError("Missing required cwd argument")

    try:
        _pre_commit_version()
    except CommandError as exc:
        raise RuntimeError("pre-commit is not installed or not found in PATH") from exc

    base_dir = get_base_dir()
    config_dir = os.path.join(base_dir, "config")

    last_run = get_last_upgrade_timestamp()
    logger.debug(f"Last pre-commit run at {last_run}")

    now = datetime.now()
    delta = timedelta(seconds=__upgrade_interval_seconds__)

    # TODO: remove this later
    if (last_run and now - last_run < delta) or True == True:
        logger.debug("Pre-commit upgrade skipped due to upgrade interval.")
    else:
        logger.debug("Running hooked self-upgrade...")
        self_upgrade()

        logger.debug("Running pre-commit autoupdate...")
        run_cmd(["pre-commit", "autoupdate"], cwd=config_dir)

        logger.debug("Updating hooked rules...")
        update_config_git_repo(base_dir)

        logger.debug("Installing latest version of hooked git hooks...")
        hooks_dir = create_hooks_dir(base_dir)
        templates_dir = create_git_template_dir(base_dir)
        copy_git_hooks("hooked.data.git_hook_templates", templates_dir)
        copy_git_hooks("hooked.data.git_hooks", hooks_dir)

        set_last_upgrade_timestamp()

    cwd_path = Path(cwd[0]).resolve()
    if not cwd_path.exists() or not cwd_path.is_dir():
        raise RuntimeError(f"Provided path {cwd} does not exist or is not a directory")

    logger.debug("Starting to work in the target repository %s...", cwd_path)

    staged_files = run_cmd(
        ["git", "diff", "--cached", "--name-only", "--diff-filter", "ACM"],
        cwd=str(cwd_path),
    ).stdout
    if not staged_files:
        logger.info("No staged files to check.")
        return 0

    logger.debug(f"Staged files: {staged_files}")
    logger.debug("Running pre-commit hooks...")
    try:
        pre_commit_config = os.path.join(config_dir, ".pre-commit-config.yaml")

        _env = os.environ.copy()
        _env["GITLEAKS_CONFIG"] = os.path.join(config_dir, ".gitleaks.toml")
        _env["PRE_COMMIT_COLOR"] = "always"

        run_stream(
            [
                "pre-commit",
                "run",
                "--config",
                pre_commit_config,
            ],
            env=_env,
            cwd=str(cwd_path),
        )
    except CommandError as exc:
        # pre-commit returns exit code 1 on "expected" failures (i.e., hook failures) and 3 for unexpected ones
        if (
            getattr(exc, "result", None)
            and getattr(exc.result, "returncode", None) == 1
        ):
            logger.warning(
                "Pre-commit hooks failed. Please fix the issues and try again."
            )
            return 1
        raise

    return 0
