import logging
import pytest

from hal.probes.base import BaseProbe
from hal.probes.exporters import logger


def test_base_probe():
    """Should be initializable with a default config."""
    probe = BaseProbe()
    assert probe.config == {"exporter": logger}
    assert probe.results is None


def test_base_probe_config():
    """Should be possible to add extra configuration."""
    probe = BaseProbe({"test": "branch", "exporter": "new"})
    assert probe.config == {"test": "branch", "exporter": "new"}


def test_base_probe_run():
    """Should raise a NotImplementedError."""
    probe = BaseProbe()
    with pytest.raises(NotImplementedError):
        probe.run()


def test_base_probe_export(caplog):
    """Should export to the logger by default."""
    probe = BaseProbe()
    probe.results = 42
    with caplog.at_level(logging.INFO):
        probe.export()

        assert len(caplog.records) == 1
        for record in caplog.records:
            assert record.levelname == "INFO"
            assert record.message == "42"


def test_base_probe_export_no_results(caplog):
    """Should log a warning if the probe has no results."""
    probe = BaseProbe()
    with caplog.at_level(logging.WARNING):
        probe.export()

        assert len(caplog.records) == 1
        for record in caplog.records:
            assert record.levelname == "WARNING"
            assert "no results are available" in record.message


def test_base_probe_custom_exporter(mocker):
    """Should allow a custom exporter via config."""
    fn = mocker.Mock()
    probe = BaseProbe({"exporter": fn})
    probe.results = 42
    probe.export()
    assert fn.call_count == 1
    assert fn.call_args == ((42,),)


def test_base_probe_bad_exporter(caplog):
    """Should log an error without raising exceptions if the exporter is not a function."""
    probe = BaseProbe({"exporter": None})
    with caplog.at_level(logging.ERROR):
        probe.export()

        assert len(caplog.records) == 1
        for record in caplog.records:
            assert record.levelname == "ERROR"
            assert "not available" in record.message
