import logging
from functools import lru_cache


class LoggingFormatter(logging.Formatter):
    """ Basic logging formatter with more information and coloring."""
    green = "\x1b[32;1m"
    yellow = "\x1b[33;1m"
    white = "\x1b[37;1m"
    red = "\x1b[31;1m"
    reset = "\x1b[0m"

    format_str = (
        f"%(levelname)-8s{reset} | "
        f"{white}%(filename)30s:%(lineno)d{reset} | "
        f"%(asctime)s{reset} | "
        f"%(message)s"
    )

    FORMATS = {
        logging.DEBUG: format_str + reset,
        logging.INFO: green + format_str + reset,
        logging.WARNING: yellow + format_str + reset,
        logging.ERROR: red + format_str + reset,
        logging.CRITICAL: red + format_str + reset
    }

    def format(self, record):
        """ Create and set the actual formatter and format."""
        log_fmt = self.FORMATS.get(record.levelno, self.format_str)
        formatter = logging.Formatter(log_fmt, datefmt="%H:%M:%S")
        return formatter.format(record)


@lru_cache
def get_logger(log_level:int):
    logger = logging.getLogger("railway")
    logger.setLevel(log_level)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(LoggingFormatter())
    logger.addHandler(stream_handler)
    return logger

def get_logger_by_level(loglevel:str):

    match loglevel:
        case 'debug':
            logger = get_logger(logging.DEBUG)
        case 'warning':
            logger = get_logger(logging.WARNING)
        case _:
            logger = get_logger(logging.INFO)

    return logger