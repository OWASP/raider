import logging

from raider.utils import colors


class CustomFormatter(logging.Formatter):
    grey = colors["GRAY-BLACK"]
    cyan = colors["CYAN-BLACK"]
    yellow = colors["YELLOW-BLACK"]
    red = colors["RED-BLACK"]
    bold_red = colors["RED-BLACK-B"]
    reset = colors["RESET"]
    format = "%(levelname)s:%(asctime)s:%(name)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: cyan + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def get_logger(loglevel, realm) -> None:
    logger = logging.getLogger(realm)
    logger.setLevel(loglevel)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(CustomFormatter())
    logger.addHandler(stream_handler)
    logger.propagate = False
    return logger
