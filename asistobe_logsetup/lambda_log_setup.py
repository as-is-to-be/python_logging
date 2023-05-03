import logging
import sys
from types import TracebackType

from logtail.frame import create_frame
from logtail.helpers import DEFAULT_CONTEXT, LogtailContext
from logtail.uploader import Uploader

DEFAULT_HOST = "https://in.logtail.com"
DEFAULT_RAISE_EXCEPTIONS = False
DEFAULT_INCLUDE_EXTRA_ATTRIBUTES = True


# The default LogtailHandler uses multiprocessing which do not work with AWS Lambda
# This log handler will choke under heavy load
class _SingleThreadedLogtailHandler(logging.Handler):
    def __init__(
        self,
        source_token: str,
        host: str = DEFAULT_HOST,
        raise_exceptions: bool = DEFAULT_RAISE_EXCEPTIONS,
        include_extra_attributes: bool = DEFAULT_INCLUDE_EXTRA_ATTRIBUTES,
        context: LogtailContext = DEFAULT_CONTEXT,
        level: int = logging.NOTSET,
    ):
        super().__init__(level=level)
        self.source_token = source_token
        self.host = host
        self.context = context
        self.uploader = Uploader(self.source_token, self.host)
        self.include_extra_attributes = include_extra_attributes
        self.raise_exceptions = raise_exceptions

    def emit(self, record: logging.LogRecord) -> None:
        try:
            message = self.format(record)
            frame = create_frame(
                record,
                message,
                self.context,
                include_extra_attributes=self.include_extra_attributes,
            )
            self.uploader(frame)
        except Exception as e:
            if self.raise_exceptions:
                raise e


def configure_lambda_logger(logtail_token: str) -> logging.Logger:
    stdout_handler = logging.StreamHandler(stream=sys.stdout)
    stdout_handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))

    logging.getLogger().handlers = []  # disable AWS root logger

    logger = logging.getLogger()
    logger.handlers = []
    logger.addHandler(stdout_handler)
    logger.setLevel(logging.INFO)

    try:
        # If this process fails, the log entry will only show up in AWS CloudWatch
        handler = _SingleThreadedLogtailHandler(source_token=logtail_token)
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
