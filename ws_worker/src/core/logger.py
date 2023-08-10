import sentry_sdk
import structlog
import structlog_sentry_logger

from src.core.config import settings

sentry_sdk.init(
    dsn=settings.sentry_dsn,
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production,
    traces_sample_rate=1.0,
)
sentry_sdk.utils.MAX_STRING_LENGTH = 8192


logger: structlog.stdlib.BoundLogger = structlog_sentry_logger.get_logger()
