import argparse


class HookedArgumentParser(argparse.ArgumentParser):
    def parse_args(self, args=None, namespace=None):
        namespace = super().parse_args(args, namespace)
        # --freeze requires rev for the 'upgrade' command
        if (
            getattr(namespace, "cmd", None) == "upgrade"
            and getattr(namespace, "freeze", False)
            and not getattr(namespace, "rev", None)
        ):
            self.error("--freeze requires a 'rev' (branch/tag/sha) to be provided")
        return namespace


def cmd_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="hooked",
        description="Does stuff with Git hooks",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--log-level",
        type=str,
        choices=["ALWAYS", "CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"],
        default=None,
        help="Log level as string.",
    )
    sub = parser.add_subparsers(dest="cmd")

    # run subcommand
    cmd_run = sub.add_parser(
        "run",
        help="run hooked hooks",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    cmd_run_sub = cmd_run.add_subparsers(dest="cmd_run")

    cmd_run_pre_commit = cmd_run_sub.add_parser(
        "pre-commit",
        help="run the pre-commit hook actions",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    cmd_run_pre_commit.add_argument(
        "path",
        type=str,
        nargs=1,
        help="Path to the repository where the pre-commit hook should be run",
    )

    # install subcommand
    cmd_install = sub.add_parser(
        "install",
        help="install hooked into your system",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    cmd_install.add_argument(
        "rules",
        type=str,
        nargs=1,
        help="Git repository URL or local path to the ruleset",
    )
    cmd_install.add_argument(
        "--branch",
        type=str,
        default="main",
        help="Branch of the ruleset repository to use",
    )

    # update rules subcommand
    cmd_update_rules = sub.add_parser(
        "update-rules",
        help="update hooked rule set",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    cmd_update_rules.add_argument(
        "--force",
        action="store_true",
        default=False,
        help="Force update by resetting local changes",
    )

    # upgrade subcommand
    cmd_upgrade = sub.add_parser("upgrade", help="Upgrade hooked installation")
    cmd_upgrade.add_argument(
        "--reset",
        action="store_true",
        help="Reset to latest semver release (stop tracking branch/SHA)",
    )
    cmd_upgrade.add_argument(
        "--freeze",
        action="store_true",
        default=False,
        help="Freezes current installation to its branch/tag/sha (stops tracking branch)",
    )
    cmd_upgrade.add_argument(
        "rev",
        type=str,
        nargs="?",
        help="Switch to given branch/tag/sha and install from there",
    )
    cmd_upgrade.add_argument(
        "--periodic",
        action="store_true",
        default=False,
        help="Indicates that this upgrade is triggered by the periodic check",
    )

    # cron subcommand
    cmd_cron = sub.add_parser(
        "cron",
        help="Serves as entrypoint to auto-update the ruleset and upgrade hooked itself",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    cmd_cron.add_argument(
        "--force",
        action="store_true",
        default=False,
        help="Ignore the timer",
    )

    # version subcommand
    sub.add_parser(
        "version",
        help="print the current version",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # uninstall subcommand
    sub.add_parser(
        "uninstall",
        help="remove hooked hooks from your system",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    return parser
