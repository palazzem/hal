import logging
import pytest

from hal.exporters.base import BaseExporter
from hal.exporters.logger import LogExporter


def test_base_interface():
    base = BaseExporter()
    with pytest.raises(NotImplementedError):
        base.send(42)


def test_log_exporter(caplog):
    """Should export data to the Python logger."""
    with caplog.at_level(logging.INFO):
        exporter = LogExporter()
        exporter.send(42)

        assert len(caplog.records) == 1
        for record in caplog.records:
            assert record.levelname == "INFO"
            assert record.message == "42"
