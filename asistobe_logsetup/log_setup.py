import logging
import sys
from types import TracebackType

from logtail import LogtailHandler

DEFAULT_HOST = "https://in.logtail.com"


def configure_logger(logtail_token: str) -> logging.Logger:
    stdout_handler = logging.StreamHandler(stream=sys.stdout)
    stdout_handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))

    logging.getLogger().handlers = []

    logger = logging.getLogger()
    logger.handlers = []
    logger.addHandler(stdout_handler)
    logger.setLevel(logging.INFO)

    try:
        handler = LogtailHandler(source_token=logtail_token)
        logger.addHandler(handler)
        logger.info("Successfully added handler for logtail")
    except Exception as e:
        print("Unknown failure while setting up logtail", e)

    logger.info("Log configuration complete")
    return logger


def handle_unhandled_exception(
    exc_type: type, exc_value: BaseException, exc_traceback: TracebackType
) -> None:
    logger = logging.getLogger()
    if issubclass(exc_type, KeyboardInterrupt):
        # Will call default excepthook
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
        # Create a critical level log message with info from the except hook.
    logger.critical("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))


# Assign the excepthook to the handler
sys.excepthook = handle_unhandled_exception
