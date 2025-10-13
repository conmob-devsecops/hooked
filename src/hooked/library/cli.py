#  Copyright 2025 T-Systems International GmbH
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are met:
#
#  1. Redistributions of source code must retain the above copyright notice, this
#     list of conditions and the following disclaimer.
#
#  2. Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#
#  3. Neither the name of the copyright holder nor the names of its
#     contributors may be used to endorse or promote products derived from
#     this software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#  AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#  IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#  DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
#  FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
#  DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#  SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
#  CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#  OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
from __future__ import annotations

import argparse

# this is a hack to figure out if the arg was set or set to default by omission
class StoreProvided(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)
        setattr(namespace, f"{self.dest}_provided", True)

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
        default="ERROR",
        action=StoreProvided,
        help="Level (default: %(default)s)",
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
