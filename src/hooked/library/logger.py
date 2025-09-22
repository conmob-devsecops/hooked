import logging

logger = logging.getLogger("hooked")
logger.setLevel(logging.WARNING)
handler = logging.StreamHandler()
formatter = logging.Formatter(
    "[hooked] %(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s"
)
handler.setFormatter(formatter)
logger.addHandler(handler)

# custom log level that is always shown, regardless of the log level set
ALWAYS = 60
logging.addLevelName(ALWAYS, "ALWAYS")


def always(self, msg, *args, **kwargs):
    self._log(ALWAYS, msg, args, **kwargs)


logging.Logger.always = always

LOG_LEVELS = {
    "ALWAYS": ALWAYS,
    "CRITICAL": logging.CRITICAL,
    "ERROR": logging.ERROR,
    "WARNING": logging.WARNING,
    "INFO": logging.INFO,
    "DEBUG": logging.DEBUG,
}


def set_log_level(verbosity: str):
    verbosity = verbosity.upper()

    if verbosity not in LOG_LEVELS:
        verbosity = "WARNING"
        logger.warning(f"Unknown log level: {verbosity}, defaulting to WARNING")

    logger.setLevel(verbosity)
