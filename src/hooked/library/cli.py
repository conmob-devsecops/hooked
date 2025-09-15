import argparse


def cmd_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='hooked',
        description='Does stuff with Git hooks',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    sub = parser.add_subparsers(dest='cmd')

    # install subcommand
    cmd_install = sub.add_parser(
        'install',
        help='install hooked into your system',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    cmd_install.add_argument(
        '--rules',
        type=str,
        required=True,
        help='Git repository URL or local path to the ruleset',
    )
    cmd_install.add_argument(
        '--branch',
        type=str,
        default='main',
        help='Branch of the ruleset repository to use',
    )

    cmd_skip_duplicates = sub.add_parser(
        'list-duplicate-hooks',
        help="List duplicate hooks between hooked and the repository's .pre-commit-config.yaml",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    cmd_skip_duplicates.add_argument(
        'path',
        type=str,
        nargs=1,
        help='Path to the .pre-commit-config.yaml file',
    )

    # update subcommand
    cmd_update = sub.add_parser(
        'update',
        help='update hooked ruleset',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    cmd_update.add_argument(
        '--force',
        action='store_true',
        default=False,
        help='Force update by resetting local changes',
    )

    # upgrade subcommand
    cmd_upgrade = sub.add_parser('upgrade', help='Upgrade hooked installation')
    cmd_upgrade.add_argument(
        '--reset',
        action='store_true',
        help='Reset to latest semver release (stop tracking branch/SHA)',
    )
    cmd_upgrade.add_argument(
        '--freeze',
        action='store_true',
        default=False,
        help='Freezes current installation to its branch/tag/sha (stop tracking branch)',
    )
    cmd_upgrade.add_argument(
        'rev',
        type=str,
        nargs='?',
        help='Switch to given branch/tag/sha and install from there',
    )

    # cron subcommand
    cmd_cron = sub.add_parser(
        'cron',
        help='Serves as entrypoint to auto-update the ruleset and upgrade hooked itself',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # version subcommand
    sub.add_parser(
        'version',
        help='print the current version',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # uninstall subcommand
    sub.add_parser(
        'uninstall',
        help='remove hooked from your system',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    return parser
