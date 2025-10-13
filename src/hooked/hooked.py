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

import os
import sys
from collections.abc import Sequence
from datetime import datetime, timedelta

from hooked import __upgrade_interval_seconds__, __version__
from hooked.library.cli import cmd_parser
from hooked.library.config import update_config_git_repo
from hooked.library.files import copy_hooked_files, get_base_dir
from hooked.library.logger import logger, set_log_level
from hooked.library.upgrade import (
    get_last_upgrade_timestamp,
    self_upgrade,
    set_last_upgrade_timestamp,
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = cmd_parser()

    args = parser.parse_args(argv)
    log_level = os.getenv("HOOKED_LOG_LEVEL", "warning")

    if args.log_level:
        log_level = args.log_level

    set_log_level(log_level)

    logger.debug(f"hooked version {__version__}")
    logger.debug(f"Arguments: {args}")
    logger.debug(f"Log level set to {logger.level}")

    if args.cmd == "version":
        sys.stdout.write(f"hooked version {__version__}\n")
        sys.stdout.flush()
        return 0

    if args.cmd == "install":
        from hooked.library.install import install

        return install(args.rules[0], branch=args.branch)

    if args.cmd == "update-rules":
        logger.debug("Updating hooked rule set...")

        base_dir = get_base_dir()
        update_config_git_repo(base_dir)
        logger.debug("Rule set updated.")

        return 0

    if args.cmd == "upgrade" and args.periodic:
        logger.debug("Running hooked periodic job...")

        last_run = get_last_upgrade_timestamp()
        now = datetime.now()
        delta = timedelta(seconds=__upgrade_interval_seconds__)
        if last_run and now - last_run < delta and not args.force:
            logger.info(
                "Last upgrade was %s, skipping upgrade (interval %s)", last_run, delta
            )
            return 0

        set_last_upgrade_timestamp()

        logger.debug("Upgrading hooked installation...")
        self_upgrade()

        logger.debug("Updating hooked ruleset...")
        update_config_git_repo(get_base_dir())

        copy_hooked_files()

        return 0

    if args.cmd == "upgrade":
        return self_upgrade(reset=args.reset, freeze=args.freeze, rev=args.rev)

    if args.cmd == "uninstall":
        from hooked.library.install import uninstall

        return uninstall()

    if args.cmd == "run" and getattr(args, "cmd_run", None) == "pre-commit":
        from hooked.library.hooks.pre_commit import run_pre_commit_hook

        return run_pre_commit_hook(args.path)

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
