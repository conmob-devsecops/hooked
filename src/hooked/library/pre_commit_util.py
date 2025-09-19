from .cmd_util import CommandError


def is_hook_error(err: CommandError) -> bool:
    """
    Checks exit code to determine if the error is due to a failed hook.

    Args:
        err (CommandError): The CommandError exception to check.
    Returns:
        bool: True if the error is due to a failed hook, False otherwise.
    """
    # pre-commit returns exit code 1 on "expected" failures (i.e., hook failures) and 3 for unexpected ones
    if getattr(err, "result", None) and getattr(err.result, "returncode", None) == 1:
        return True
    return False
