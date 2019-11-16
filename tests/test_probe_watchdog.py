import pytest
import logging

from hal.probes.watchdog import WatchdogProbe


def test_watchdog_probe():
    """Should be initialized with a default config."""
    probe = WatchdogProbe()
    assert probe.config["hosts"] == []


def test_watchdog_run_without_hosts(caplog):
    """Should fail if hosts are not defined."""
    probe = WatchdogProbe()
    with caplog.at_level(logging.ERROR):
        result = probe.run()

        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert record.levelname == "ERROR"
        assert "run failed for missing hosts" in record.message
        assert result is False


def test_watchdog_success(mocker):
    """Should succeed with valid hosts to monitor."""
    process = mocker.patch("subprocess.run")
    process.return_value.returncode = 0
    probe = WatchdogProbe({"hosts": ["127.0.0.1"]})
    probe.run()
    assert len(probe.results) == 1
    assert probe.results["hal.watchdog.detected_hosts"] == 1


def test_watchdog_multiple_hosts(mocker):
    """Should detect multiple hosts."""
    process = mocker.patch("subprocess.run")
    process.return_value.returncode = 0
    probe = WatchdogProbe({"hosts": ["127.0.0.1", "127.0.0.1"]})
    probe.run()
    assert len(probe.results) == 1
    assert probe.results["hal.watchdog.detected_hosts"] == 2


def test_watchdog_partial_failure(mocker):
    """Should report only detected hosts."""
    process = mocker.patch("subprocess.run")
    type(process.return_value).returncode = mocker.PropertyMock(side_effect=[0, 1])
    probe = WatchdogProbe({"hosts": ["127.0.0.1", "invalid-host"]})
    probe.run()
    assert len(probe.results) == 1
    assert probe.results["hal.watchdog.detected_hosts"] == 1


@pytest.mark.xfail
def test_watchdog_partial_failure_integration(mocker):
    """Should report only detected hosts. This test runs the `ping` command,
    but in some CI it can fail to prevent DoS. Because of that, the test
    is marked as it can fail.
    """
    probe = WatchdogProbe({"hosts": ["127.0.0.1", "invalid-host"]})
    probe.run()
    assert len(probe.results) == 1
    assert probe.results["hal.watchdog.detected_hosts"] == 1


def test_watchdog_failure(caplog, mocker):
    """Should log a debug entry if it fails."""
    process = mocker.patch("subprocess.run")
    process.return_value.returncode = 1
    probe = WatchdogProbe({"hosts": ["invalid-host"]})
    with caplog.at_level(logging.DEBUG):
        result = probe.run()

        assert len(caplog.records) == 3
        record = caplog.records[1]
        assert record.levelname == "DEBUG"
        assert "Probe watchdog: host 'invalid-host' not found" in record.message
        assert result is True
        assert probe.results["hal.watchdog.detected_hosts"] == 0
