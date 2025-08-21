import logging
import logging.config


def setup_logging(default_level=logging.INFO, log_config: dict = None):
    if log_config:
        logging.config.dictConfig(log_config)
    else:
        logging.basicConfig(level=default_level)


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": "INFO",
        },
        "file": {
            "class": "logging.FileHandler",
            "formatter": "standard",
            "level": "DEBUG",
            "filename": "app.log"
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "DEBUG",
    }
}
