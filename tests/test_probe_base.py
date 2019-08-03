import logging
import pytest

from hal.probes.base import BaseProbe


def test_base_probe():
    """Should be initializable with a default config."""
    probe = BaseProbe()
    assert len(probe.config["exporters"]) == 0
    assert probe.results is None


def test_base_probe_config():
    """Should be possible to add extra configuration."""
    probe = BaseProbe({"test": "branch", "exporters": []})
    assert probe.config == {"test": "branch", "exporters": []}


def test_base_probe_with_defaults():
    """Should be possible to add extra configuration that overrides defaults hierarchy."""
    defaults = {"test": "branch"}
    config = {"exporters": []}
    probe = BaseProbe(config=config, defaults=defaults)
    assert probe.config == {"test": "branch", "exporters": []}


def test_base_probe_run():
    """Should raise a NotImplementedError."""
    probe = BaseProbe()
    with pytest.raises(NotImplementedError):
        probe.run()


def test_base_probe_custom_exporter(mocker):
    """Should allow a custom exporter via config."""
    exporter = mocker.Mock()
    probe = BaseProbe({"exporters": [exporter]})
    probe.results = 42
    probe.export()
    assert exporter.send.call_count == 1
    assert exporter.send.call_args == ((42,),)


def test_base_probe_export_no_results(caplog):
    """Should log a warning if the probe has no results."""
    probe = BaseProbe()
    with caplog.at_level(logging.WARNING):
        probe.export()

        assert len(caplog.records) == 1
        for record in caplog.records:
            assert record.levelname == "WARNING"
            assert "no results are available" in record.message


def test_base_probe_bad_exporter(caplog):
    """Should log an error without raising exceptions if the exporter is not valid."""
    probe = BaseProbe({"exporters": None})
    with caplog.at_level(logging.ERROR):
        probe.export()

        assert len(caplog.records) == 1
        for record in caplog.records:
            assert record.levelname == "ERROR"
            assert "not available" in record.message
