import logging
import sys
import json
from datetime import datetime, timezone


class JSONFormatter(logging.Formatter):
    """Structured JSON formatter for production and audit logging."""
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        if hasattr(record, "extra_data"):
            log_entry["data"] = record.extra_data
        return json.dumps(log_entry)


def setup_logging(environment: str = "development") -> logging.Logger:
    logger = logging.getLogger("fashionpulse")
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        if environment == "production":
            handler.setFormatter(JSONFormatter())
        else:
            handler.setFormatter(logging.Formatter(
                "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s"
            ))
        logger.addHandler(handler)
        
    return logger


logger = setup_logging()
