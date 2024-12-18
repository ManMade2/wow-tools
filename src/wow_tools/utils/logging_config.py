import logging
from pythonjsonlogger.json import JsonFormatter


def setup_logging():
    """
    Sets up logging to use JSON format.
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    formatter = JsonFormatter("{asctime} {levelname} {message}", style="{", json_indent=4)

    file_handler = logging.FileHandler("app.log")
    file_handler.setFormatter(formatter)
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.addHandler(file_handler)
