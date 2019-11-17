import logging

from requests.exceptions import HTTPError

from hal.probes.elmo import ElmoProbe


def test_elmo_probe():
    """Should be initialized with a default config."""
    probe = ElmoProbe()
    assert probe.config["base_url"] is None
    assert probe.config["vendor"] is None
    assert probe.config["username"] is None
    assert probe.config["password"] is None


def test_elmo_without_base_url(caplog):
    """Should fail if base_url is not defined."""
    probe = ElmoProbe()
    with caplog.at_level(logging.ERROR):
        result = probe.run()

        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert record.levelname == "ERROR"
        assert "missing 'base_url' and 'vendor'" in record.message
        assert result is False


def test_elmo_without_vendor(caplog):
    """Should fail if vendor is not defined."""
    probe = ElmoProbe({"base_url": "https://example.com"})
    with caplog.at_level(logging.ERROR):
        result = probe.run()

        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert record.levelname == "ERROR"
        assert "missing 'base_url' and 'vendor'" in record.message
        assert result is False


def test_elmo_without_username(caplog):
    """Should fail if username is not defined."""
    probe = ElmoProbe({"base_url": "https://example.com", "vendor": "vendor"})
    with caplog.at_level(logging.ERROR):
        result = probe.run()

        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert record.levelname == "ERROR"
        assert "missing credentials" in record.message
        assert result is False


def test_elmo_without_password(caplog):
    """Should fail if password is not defined."""
    probe = ElmoProbe(
        {"base_url": "https://example.com", "vendor": "vendor", "username": "user"}
    )
    with caplog.at_level(logging.ERROR):
        result = probe.run()

        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert record.levelname == "ERROR"
        assert "missing credentials" in record.message
        assert result is False


def test_elmo_success(mocker):
    """Should collect metrics using the ElmoClient."""
    probe = ElmoProbe(
        {
            "base_url": "https://example.com",
            "vendor": "vendor",
            "username": "user",
            "password": "pass",
        }
    )
    client = mocker.patch("hal.probes.elmo.ElmoClient")
    client().check.return_value = {
        "areas_armed": [{"id": 0, "name": "Entryway"}],
        "areas_disarmed": [{"id": 1, "name": "Kitchen"}],
        "inputs_alerted": [{"id": 0, "name": "Door"}],
        "inputs_wait": [{"id": 1, "name": "Window"}],
    }
    assert probe.run() is True
    assert len(probe.results) == 2
    assert probe.results["hal.elmo.areas"] == [
        (1, ["name:Entryway", "status:armed"]),
        (1, ["name:Kitchen", "status:disarmed"]),
    ]
    assert probe.results["hal.elmo.inputs"] == [
        (1, ["name:Door", "status:alerted"]),
        (1, ["name:Window", "status:wait"]),
    ]


def test_elmo_fail_api_calls(mocker, caplog):
    """Should log if ElmoClient is unable to retrieve the system status."""
    probe = ElmoProbe(
        {
            "base_url": "https://example.com",
            "vendor": "vendor",
            "username": "user",
            "password": "pass",
        }
    )
    client = mocker.patch("hal.probes.elmo.ElmoClient")
    client().check.side_effect = mocker.Mock(side_effect=HTTPError("403"))
    with caplog.at_level(logging.ERROR):
        assert probe.run() is False
        assert len(probe.results) == 0

        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert record.levelname == "ERROR"
        assert "ElmoClient returns '403'" in record.message
