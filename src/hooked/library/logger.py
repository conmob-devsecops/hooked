import logging

logger = logging.getLogger("hooked")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter(
    "%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s"
)
handler.setFormatter(formatter)
logger.addHandler(handler)
