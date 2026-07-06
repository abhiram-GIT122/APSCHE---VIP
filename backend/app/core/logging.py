import logging
import sys
from app.config.config import settings

def setup_logging():
    """Sets up standard Python logging configurations."""
    log_level = logging.INFO
    if settings.ENVIRONMENT == "development":
        log_level = logging.DEBUG

    # Define root logger configuration
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d) - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

    # Specific logger overrides (if needed to reduce external package noise)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    logger = logging.getLogger("app")
    logger.info(f"Logging initialized with level: {logging.getLevelName(log_level)}")
