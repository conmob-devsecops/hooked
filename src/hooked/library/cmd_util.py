import shlex
import signal
import subprocess as sp
import sys
import threading
from dataclasses import dataclass
from typing import Optional, Sequence, Mapping, List

from logging import DEBUG

from .logger import logger


@dataclass
class CommandResult:
    cmd: Sequence[str]
    returncode: int
    stdout: Optional[str]
    stderr: Optional[str]

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
) -> None:
    """Log stderr AND stdout when a command fails, then raise CommandError."""
    if result.stderr and stderr:
        logger.error("stderr:\n%s", result.stderr)
    if result.stdout and stdout:
        logger.error("stdout:\n%s", result.stdout)
    raise CommandError(result)


def run_cmd(
    cmd: Sequence[str],
    *,
    timeout: Optional[float] = None,
    cwd: Optional[str] = None,
    env: Optional[Mapping[str, str]] = None,
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
        _handle_failure(CommandResult(cmd, 127, None, str(e)), stderr=True, stdout=True)
    except sp.TimeoutExpired as e:
        rc = -signal.SIGALRM
        _handle_failure(CommandResult(cmd, rc, e.stdout, e.stderr))

    result = CommandResult(
        cmd, completed.returncode, completed.stdout.strip(), completed.stderr.strip()
    )
    if not result.ok:
        _handle_failure(result)
    return result


def run_stream(
    cmd: Sequence[str],
    *,
    cwd: Optional[str] = None,
    env: Optional[Mapping[str, str]] = None,
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
        _handle_failure(CommandResult(cmd, 127, None, str(e)))

    out_buf: List[str] = []
    err_buf: List[str] = []

    def _pump(src, dst, collector: List[str]):
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
        cmd,
        rc,
        "".join(out_buf) if out_buf else None,
        "".join(err_buf) if err_buf else None,
    )
    if not result.ok:
        _handle_failure(result)
    return result


def exit_with_child_status(returncode: int):
    """Exit current process with the normalized child status."""
    sys.exit(_normalize_exit_code(returncode))
