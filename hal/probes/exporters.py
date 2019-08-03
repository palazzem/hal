import logging


log = logging.getLogger(__name__)


def logger(results):
    """Exports probe results using the default logger.

    Args:
        results: probe collected results.
    """
    log.info(results)
