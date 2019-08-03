import logging

from .base import BaseExporter


log = logging.getLogger(__name__)


class LogExporter(BaseExporter):
    """LogExporter sends data using the Python logger."""

    def send(self, data):
        log.info(data)
