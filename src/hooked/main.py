from __future__ import annotations

import sys
from collections.abc import Sequence

from hooked import __version__
from hooked.library import (
    cmd_parser,
    copy_git_hook_templates,
    copy_git_hooks,
    create_base_dir,
    create_git_template_dir,
    create_hooks_dir,
    get_base_dir,
    get_config_git_repo,
    git_set_global_hook_path,
    git_set_template_dir,
    git_unset_global_hook_path,
    git_unset_template_dir,
    remove_base_dir,
    update_config_git_repo,
    self_upgrade,
    logger,
    pre_commit_diff
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

        copy_git_hooks(hooks_dir)
        logger.debug('Git hooks copied.')

        get_config_git_repo(base_dir, args.rules, args.branch)
        logger.debug('Pre-commit config installed.')

        copy_git_hook_templates(templates_dir)
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

    if args.cmd == 'upgrade' and args.pin and not args.switch:
        parser.error('--pin can only be used with --switch')

    if args.cmd == 'upgrade':
        return self_upgrade(reset=args.reset, pin=args.pin, switch=args.switch)

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
