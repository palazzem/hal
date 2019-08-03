import datadog
import logging
import pytest

from hal.exporters.base import BaseExporter
from hal.exporters.datadog import DatadogExporter
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


def test_datadog_exporter_client_config(mocker):
    """Should configure Datadog client with the given API_KEY."""
    mocker.patch("datadog.initialize")
    DatadogExporter({"api_key": "test_api_key"})
    assert datadog.initialize.call_count == 1
    assert datadog.initialize.call_args == ({"api_key": "test_api_key"},)


def test_datadog_exporter_missing_api_key(caplog):
    """Should log an error if the API_KEY is not configured."""
    with caplog.at_level(logging.ERROR):
        exporter = DatadogExporter()
        exporter.send(42)

        assert len(caplog.records) == 1
        for record in caplog.records:
            assert record.levelname == "ERROR"
            assert "api_key is not configured" in record.message


def test_datadog_exporter_send(mocker):
    """Should send probe data to Datadog."""
    mocker.patch("datadog.api.Metric.send").return_value = {"status": "ok"}
    exporter = DatadogExporter(
        {"api_key": "valid", "hostname": "home", "tags": "automation"}
    )
    exporter.send({"metric_1": 1, "metric_2": 2})

    # Two different metrics must be sent
    assert datadog.api.Metric.send.call_count == 2
    _, kwargs = datadog.api.Metric.send.call_args_list[0]
    assert kwargs == {
        "host": "home",
        "metric": "metric_1",
        "points": 1,
        "tags": "automation",
    }
    _, kwargs = datadog.api.Metric.send.call_args_list[1]
    assert kwargs == {
        "host": "home",
        "metric": "metric_2",
        "points": 2,
        "tags": "automation",
    }


def test_datadog_exporter_send_fail(mocker, caplog):
    """Should log an error if the response is not a 200."""
    mocker.patch("datadog.api.Metric.send").return_value = {"status": "error"}
    with caplog.at_level(logging.ERROR):
        exporter = DatadogExporter({"api_key": "valid"})
        exporter.send({"metric_1": 1})

        assert len(caplog.records) == 1
        for record in caplog.records:
            assert record.levelname == "ERROR"
            assert "unable to send metric" in record.message
