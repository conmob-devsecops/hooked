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

import logging
import os
import sys
import traceback
from argparse import Namespace
from collections.abc import Sequence

from hooked import __upgrade_interval_seconds__, __version__
from hooked.library.cli import cmd_parser
from hooked.library.config import update_config
from hooked.library.files import get_base_dir
from hooked.library.logger import logger, set_log_level


def main(argv: Sequence[str] | None = None):
    parser = cmd_parser()

    args = parser.parse_args(argv)

    # default log level is ERROR, can be overridden by HOOKED_LOG_LEVEL env var
    log_level = os.getenv("HOOKED_LOG_LEVEL", "info").upper()

    # override log level if --log-level was provided
    if getattr(args, "log_level_provided", True):
        log_level = args.log_level.upper()

    set_log_level(log_level)

    logger.debug(f"Hooked version: {__version__}")
    logger.debug(f"Arguments: {args}")
    logger.debug(f"Log level set to {logger.level}")

    try:
        run(args)
        return os.EX_OK
    except:
        if logger.level == logging.DEBUG:
            sys.stderr.write("\033[31m")
            sys.stderr.write(traceback.format_exc())
            sys.stderr.write("\033[0m")
            sys.stderr.flush()
        return os.EX_SOFTWARE


def run(args: Namespace):
    match args.cmd:
        case "version":
            sys.stdout.write(f"Hooked version: {__version__}\n")
            sys.stdout.flush()

        case "update":
            base_dir = get_base_dir()
            update_config(base_dir)

        case "self-upgrade":
            from hooked.library.upgrade import self_upgrade

            self_upgrade(reset=args.reset, freeze=args.freeze, rev=args.rev)

        case "install":
            from hooked.library.install import check_pre_requisites, install

            check_pre_requisites()
            install(args.rules[0], branch=args.branch)

        case "disable":
            from hooked.library.install import disable

            disable(args.prune)

        case "enable":
            from hooked.library.install import check_pre_requisites, enable

            check_pre_requisites()
            enable()

        case "run":
            if getattr(args, "cmd_run", None) != "pre-commit":
                logger.error("run can only be invoked with pre-commit")
                raise NotImplementedError()

            from hooked.library.hooks.pre_commit import run_pre_commit_hook

            run_pre_commit_hook(args.path)

        case "check":
            from hooked.library.install import check_pre_requisites

            check_pre_requisites()

        case _:
            cmd_parser().print_help()


if __name__ == "__main__":
    raise SystemExit(main())
