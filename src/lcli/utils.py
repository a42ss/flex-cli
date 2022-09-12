import logging


def setup_logger(name: str, verbosity: int, file: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(verbosity)
    handler = logging.FileHandler(file)
    handler.setLevel(verbosity)
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s " "%(levelname)-8s " "%(name)s: %(message)s",
            "%Y-%m-%d %H:%M:%S",
        )
    )
    logger.addHandler(handler)
    return logger
