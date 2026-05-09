# logger_config.py
import logging


def setup_logging():
    formatter = logging.Formatter(
        "%(levelname)s: %(name)s | %(message)s", "%Y-%m-%d %H:%M:%S"
    )

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)

    logging.basicConfig(level=logging.INFO, handlers=[console])
