from __future__ import annotations

import sys
from collections.abc import Sequence
from datetime import timedelta, datetime

from hooked import __version__, __upgrade_interval_seconds__
from hooked.library.cli import cmd_parser
from hooked.library.config import get_config_git_repo, update_config_git_repo
from hooked.library.files import (
    get_base_dir,
    create_base_dir,
    create_hooks_dir,
    copy_git_hooks,
    remove_base_dir,
    create_git_template_dir,
)
from hooked.library.git import (
    git_set_global_hook_path,
    git_unset_global_hook_path,
    git_set_template_dir,
    git_unset_template_dir,
)
from hooked.library.logger import logger
from hooked.library.pre_commit_diff import pre_commit_diff
from hooked.library.upgrade import (
    self_upgrade,
    get_last_upgrade_timestamp,
    set_last_upgrade_timestamp,
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = cmd_parser()

    args = parser.parse_args(argv)

    if args.cmd == 'version':
        logger.info(f"hooked version {__version__}")
        return 0

    if args.cmd == 'install':
        logger.debug('Installing hooked...')

        base_dir = get_base_dir()
        create_base_dir(base_dir)
        logger.debug(f"Base directory created at {base_dir}")
        hooks_dir = create_hooks_dir(base_dir)
        logger.debug(f"Hooks directory created at {hooks_dir}")
        templates_dir = create_git_template_dir(base_dir)
        logger.debug(f"Git templates directory created at {templates_dir}")

        copy_git_hooks('hooked.data.git_hooks', hooks_dir)
        logger.debug('Git hooks copied.')

        get_config_git_repo(base_dir, args.rules, args.branch)
        logger.debug('Pre-commit config installed.')

        copy_git_hooks('hooked.data.git_hook_templates', templates_dir)
        logger.debug('Git templates copied.')

        git_set_global_hook_path(hooks_dir)
        logger.debug('Set Git global hooks path.')

        git_set_template_dir(templates_dir)
        logger.debug('Set Git global template directory.')

        return 0

    if args.cmd == 'list-duplicate-hooks':
        path = args.path
        diff = pre_commit_diff(path[0])
        sys.stdout.write(diff)
        sys.stdout.flush()
        return 0

    if args.cmd == 'update':
        logger.debug('Updating hooked...')

        base_dir = get_base_dir()
        update_config_git_repo(base_dir)
        logger.debug('Pre-commit config updated.')

        return 0

    if args.cmd == 'upgrade' and args.freeze and not args.rev:
        parser.error('--freeze can only be used with explicit revision argument')

    if args.cmd == 'upgrade':
        return self_upgrade(reset=args.reset, freeze=args.freeze, rev=args.rev)

    if args.cmd == 'cron':
        logger.debug('Running hooked cron job...')

        base_dir = get_base_dir()

        last_run = get_last_upgrade_timestamp()
        now = datetime.now()
        delta = timedelta(seconds=__upgrade_interval_seconds__)
        if last_run and now - last_run < delta:
            logger.debug(
                'Last upgrade was %s, skipping upgrade (interval %s)', last_run, delta
            )
            return 0

        set_last_upgrade_timestamp()

        logger.debug('Upgrading hooked installation...')
        self_upgrade()

        logger.debug('Updating hooked ruleset...')
        update_config_git_repo(base_dir)

        get_config_git_repo(base_dir, args.rules, args.branch)
        logger.debug('Pre-commit config installed.')

        hooks_dir = create_hooks_dir(base_dir)
        templates_dir = create_git_template_dir(base_dir)
        copy_git_hooks('hooked.data.git_hook_templates', templates_dir)
        copy_git_hooks('hooked.data.git_hooks', hooks_dir)

        return 0

    if args.cmd == 'uninstall':
        logger.debug('Uninstalling hooked...')

        base_dir = get_base_dir()
        remove_base_dir(base_dir)
        logger.debug('Config directory removed.')
        git_unset_global_hook_path()
        logger.debug('Reset Git global hooks path.')
        git_unset_template_dir()
        logger.debug('Reset Git global template directory.')

        logger.debug('hooked uninstalled.')
        return 0

    parser.print_help()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
