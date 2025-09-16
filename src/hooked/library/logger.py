import logging

logger = logging.getLogger("hooked")
logger.setLevel(logging.ERROR)
handler = logging.StreamHandler()
formatter = logging.Formatter(
    "%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s"
)
handler.setFormatter(formatter)
logger.addHandler(handler)


def set_log_level(verbosity):
    levels = {
        0: logging.ERROR,
        1: logging.WARNING,
        2: logging.INFO,
        3: logging.DEBUG,
    }
    level = levels.get(verbosity, logging.DEBUG)
    logger.setLevel(level)
