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


def test_watchdog_success():
    """Should succeed with valid hosts to monitor."""
    probe = WatchdogProbe({"hosts": ["127.0.0.1"]})
    probe.run()
    assert len(probe.results) == 1
    assert probe.results["hal.watchdog.detected_hosts"] == 1


def test_watchdog_multiple_hosts():
    """Should detect multiple hosts."""
    probe = WatchdogProbe({"hosts": ["127.0.0.1", "127.0.0.1"]})
    probe.run()
    assert len(probe.results) == 1
    assert probe.results["hal.watchdog.detected_hosts"] == 2


def test_watchdog_partial_failure():
    """Should report only detected hosts."""
    probe = WatchdogProbe({"hosts": ["127.0.0.1", "invalid-host"]})
    probe.run()
    assert len(probe.results) == 1
    assert probe.results["hal.watchdog.detected_hosts"] == 1


def test_watchdog_failure(caplog):
    """Should log a debug entry if it fails."""
    probe = WatchdogProbe({"hosts": ["invalid-host"]})
    with caplog.at_level(logging.DEBUG):
        result = probe.run()

        assert len(caplog.records) == 3
        record = caplog.records[1]
        assert record.levelname == "DEBUG"
        assert "Probe watchdog: host 'invalid-host' not found" in record.message
        assert result is True
        assert probe.results["hal.watchdog.detected_hosts"] == 0
