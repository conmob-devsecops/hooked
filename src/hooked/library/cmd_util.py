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

import shlex
import signal
import subprocess as sp
import sys
import threading
from dataclasses import dataclass
from logging import DEBUG
from typing import Mapping, Sequence

from hooked.library.logger import logger


@dataclass
class CommandResult:
    cmd: Sequence[str]
    returncode: int
    stdout: str | None
    stderr: str | None

    @property
    def ok(self) -> bool:
        return self.returncode == 0


class CommandError(RuntimeError):
    def __init__(self, result: CommandResult):
        rc = result.returncode
        if rc < 0:
            msg = f"Command {result.cmd!r} terminated by signal {-rc}"
        else:
            msg = f"Command {result.cmd!r} exited with code {rc}"
        super().__init__(msg)
        self.result = result


def _normalize_exit_code(returncode: int) -> int:
    """Match shell behavior: signal N → 128+N"""
    if returncode < 0:
        return 128 + (-returncode)
    return returncode


def _log_cmd(cmd: Sequence[str]) -> None:
    """Log the command like `set -x` when in DEBUG level."""
    if logger.isEnabledFor(DEBUG):
        logger.debug("+ %s", " ".join(shlex.quote(str(arg)) for arg in cmd))


def _handle_failure(
    result: CommandResult, stderr: bool = False, stdout: bool = False
) -> CommandError:
    """Log stderr AND stdout when a command fails, then returns CommandError."""
    if result.stderr and stderr:
        logger.error("stderr:\n%s", result.stderr)
    if result.stdout and stdout:
        logger.error("stdout:\n%s", result.stdout)
    return CommandError(result)


def run_cmd(
    cmd: Sequence[str],
    *,
    timeout: float | None = None,
    cwd: str | None = None,
    env: Mapping[str, str] | None = None,
    text: bool = True,
) -> CommandResult:
    """
    Run a command (list of args). Captures stdout/stderr.
    On non-zero exit: logs stderr+stdout and raises CommandError.
    Returns CommandResult on success.
    """
    _log_cmd(cmd)
    try:
        completed = sp.run(
            cmd,
            stdout=sp.PIPE,
            stderr=sp.PIPE,
            text=text,
            timeout=timeout,
            cwd=cwd,
            env=env,
            check=False,
        )
    except FileNotFoundError as e:
        raise _handle_failure(
            CommandResult(cmd=cmd, returncode=127, stdout=None, stderr=str(e)),
            stderr=True,
            stdout=True,
        )
    except sp.TimeoutExpired as e:
        rc = -signal.SIGALRM
        raise _handle_failure(
            CommandResult(
                cmd=cmd, returncode=rc, stdout=str(e.stdout), stderr=str(e.stderr)
            )
        )

    result = CommandResult(
        cmd=cmd,
        returncode=completed.returncode,
        stdout=completed.stdout.strip(),
        stderr=completed.stderr.strip(),
    )
    if not result.ok:
        raise _handle_failure(result)
    return result


def run_stream(
    cmd: Sequence[str],
    *,
    cwd: str | None = None,
    env: Mapping[str, str] | None = None,
) -> CommandResult:
    """
    Stream output live to the console (tee) while capturing it.
    On non-zero exit: logs stderr+stdout and raises CommandError.
    Returns CommandResult on success (stdout/stderr are the captured streams).
    """
    _log_cmd(cmd)
    try:
        p = sp.Popen(
            cmd,
            cwd=cwd,
            env=env,
            stdout=sp.PIPE,
            stderr=sp.PIPE,
            text=True,
            bufsize=1,  # line-buffered
        )
    except FileNotFoundError as e:
        raise _handle_failure(
            CommandResult(cmd=cmd, returncode=127, stdout=None, stderr=str(e))
        )

    out_buf: list[str] = []
    err_buf: list[str] = []

    def _pump(src, dst, collector: list[str]):
        for line in iter(src.readline, ""):
            collector.append(line)
            try:
                dst.write(line)
                dst.flush()
            except Exception:  # noqa
                pass
        src.close()

    t_out = threading.Thread(
        target=_pump, args=(p.stdout, sys.stdout, out_buf), daemon=True
    )
    t_err = threading.Thread(
        target=_pump, args=(p.stderr, sys.stdout, err_buf), daemon=True
    )
    t_out.start()
    t_err.start()
    rc = p.wait()
    t_out.join()
    t_err.join()

    result = CommandResult(
        cmd=cmd,
        returncode=rc,
        stdout="".join(out_buf) if out_buf else None,
        stderr="".join(err_buf) if err_buf else None,
    )
    if not result.ok:
        raise _handle_failure(result)
    return result


def exit_with_child_status(returncode: int):
    """Exit current process with the normalized child status."""
    sys.exit(_normalize_exit_code(returncode))
