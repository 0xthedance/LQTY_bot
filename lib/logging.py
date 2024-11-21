import logging.config

import os


LOG_EMAIL = os.environ["LOG_EMAIL"]
EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "{asctime} - {levelname} - {message}",
            "style": "{",
            "datefmt": "%Y-%m-%d %H:%M",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "default",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.FileHandler",
            "level": "INFO",
            "formatter": "default",
            "filename": "bot.log",
        },
        "mail": {
            "class": "logging.handlers.SMTPHandler",
            "level": "ERROR",
            "formatter": "default",
            "mailhost": ("smtp.gmail.com", 25),
            "fromaddr": LOG_EMAIL,
            "toaddrs": ["thedance@amamu.io"],
            "subject": "Critical Error Log",
            "credentials": (LOG_EMAIL, EMAIL_PASSWORD),
            "secure": (),
        },
    },
    "loggers": {
        "my_logger": {
            "level": "DEBUG",
            "handlers": ["console", "file", "mail"],
            "propagate": False,
        },
    },
    "root": {
        "level": "DEBUG",
        "handlers": ["file"],
    },
}


def configure_logging():
    """Function to configure the bot logger"""
    logging.config.dictConfig(LOGGING_CONFIG)
    logger = logging.getLogger("my_logger")
    logger.info("logger configured")
    return logger
