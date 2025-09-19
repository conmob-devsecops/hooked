import logging
import os

logger = logging.getLogger("hooked")
logger.setLevel(logging.WARNING)
handler = logging.StreamHandler()
formatter = logging.Formatter(
    "[hooked]" "%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s"
)
handler.setFormatter(formatter)
logger.addHandler(handler)

# custom log level that is always shown, regardless of the log level set
ALWAYS = 60
logging.addLevelName(ALWAYS, "ALWAYS")


def always(self, msg, *args, **kwargs):
    self._log(ALWAYS, msg, args, **kwargs)


logging.Logger.always = always


def _get_level_env() -> int | None:
    level_str = (os.getenv("HOOKED_LOG_LEVEL") or "").upper()

    match level_str:
        case "INFO":
            return 1
        case "DEBUG":
            return 2
        case _:
            return None


def set_log_level(verbosity):
    if verbosity == 0 and (env_level := _get_level_env()) is not None:
        verbosity = env_level

    levels = {
        0: logging.WARNING,
        1: logging.INFO,
        2: logging.DEBUG,
    }
    level = levels.get(verbosity, logging.DEBUG)
    logger.setLevel(level)
