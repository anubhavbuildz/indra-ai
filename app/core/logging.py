"""Safe application logging configuration."""

import logging


def configure_logging(debug: bool = False) -> None:
    """Configure concise logs without request bodies or credential values."""
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        force=True,
    )
