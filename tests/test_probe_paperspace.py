import logging
import responses

from hal.probes.paperspace import PaperspaceProbe


def test_paperspace_probe():
    """Should be initialized with a default config."""
    probe = PaperspaceProbe()
    assert probe.config["api_key"] is None
    assert probe.config["base_url"] == "https://api.paperspace.io"
    assert probe.config["header_key"] == "x-api-key"


def test_paperspace_run_without_api_key(caplog):
    """Should fail if the API key is not provided."""
    probe = PaperspaceProbe()
    with caplog.at_level(logging.ERROR):
        result = probe.run()

        assert len(caplog.records) == 1
        for record in caplog.records:
            assert record.levelname == "ERROR"
            assert "missing Paperspace API key" in record.message
            assert result is False


def test_paperspace_success(server):
    """Should succeed with a valid API key."""
    machines_list = """
      [{"id": "unique_id",
        "name": "Hal 9000",
        "os": "Microsoft Windows Server 2016 Datacenter",
        "ram": "32212246528",
        "cpus": 8,
        "gpu": "Quadro P5000",
        "storageTotal": "268435456000",
        "storageUsed": "70947229184",
        "usageRate": "P5000 hourly",
        "shutdownTimeoutInHours": null,
        "shutdownTimeoutForces": false,
        "performAutoSnapshot": false,
        "autoSnapshotFrequency": null,
        "autoSnapshotSaveCount": null,
        "dynamicPublicIp": false,
        "agentType": "WindowsDesktop",
        "dtCreated": "2019-09-02T17:11:36.374Z",
        "state": "off",
        "updatesPending": false,
        "networkId": "unique_id",
        "privateIpAddress": "x.x.x.x",
        "publicIpAddress": "x.x.x.x",
        "region": "Europe (AMS1)",
        "userId": "unique_id",
        "teamId": "unique_id",
        "scriptId": null,
        "dtLastRun": null}]
    """
    machine_utilization = """
      {"machineId": "unique_id",
       "utilization": {"machineId": "unique_id",
        "secondsUsed": 23808.9384539127,
        "hourlyRate": "0.78",
        "billingMonth": "2019-09"},
       "storageUtilization": {"machineId": "unique_id",
        "secondsUsed": 416854.609315872,
        "monthlyRate": "10.00",
        "billingMonth": "2019-09"}}
    """
    server.add(
        responses.GET,
        "https://api.paperspace.io/machines/getMachines",
        body=machines_list,
        status=200,
    )
    server.add(
        responses.GET,
        "https://api.paperspace.io/machines/getUtilization",
        body=machine_utilization,
        status=200,
    )
    probe = PaperspaceProbe({"api_key": "valid"})
    probe.run()
    assert len(probe.results) == 5
    assert probe.results["hal.paperspace.machines.count"] == 1
    assert probe.results["hal.paperspace.machines.instance"] == [
        (1, ["machine_id:unique_id", "state:off"]),
        (0, ["machine_id:unique_id", "state:ready"]),
    ]
    assert probe.results["hal.paperspace.utilization.instance.usage_seconds"] == [
        (23808, ["machine_id:unique_id"])
    ]
    assert probe.results["hal.paperspace.utilization.instance.hourly_rate"] == [
        (0.78, ["machine_id:unique_id"])
    ]
    assert probe.results["hal.paperspace.utilization.storage.monthly_rate"] == [
        (10.0, ["machine_id:unique_id"])
    ]


def test_paperspace_transition_state(server):
    """Should emit an extra metric if a transition state is active."""
    machines_list = """
      [{"id": "unique_id",
        "state": "starting"}]
    """
    machine_utilization = """
      {"machineId": "unique_id",
       "utilization": {"machineId": "unique_id",
        "secondsUsed": 23808.9384539127,
        "hourlyRate": "0.78",
        "billingMonth": "2019-09"},
       "storageUtilization": {"machineId": "unique_id",
        "secondsUsed": 416854.609315872,
        "monthlyRate": "10.00",
        "billingMonth": "2019-09"}}
    """
    server.add(
        responses.GET,
        "https://api.paperspace.io/machines/getMachines",
        body=machines_list,
        status=200,
    )
    server.add(
        responses.GET,
        "https://api.paperspace.io/machines/getUtilization",
        body=machine_utilization,
        status=200,
    )
    probe = PaperspaceProbe({"api_key": "valid"})
    probe.run()
    assert len(probe.results) == 5
    assert probe.results["hal.paperspace.machines.count"] == 1
    assert probe.results["hal.paperspace.machines.instance"] == [
        (0, ["machine_id:unique_id", "state:off"]),
        (0, ["machine_id:unique_id", "state:ready"]),
        (1, ["machine_id:unique_id", "state:starting"]),
    ]


def test_paperspace_fail(server, caplog):
    """Should fail if an invalid API key is used."""
    server.add(
        responses.GET,
        "https://api.paperspace.io/machines/getMachines",
        body='{"status": 401, "message": "No such API token"}',
        status=401,
    )
    probe = PaperspaceProbe({"api_key": "invalid"})
    with caplog.at_level(logging.ERROR):
        probe.run()

        assert probe.results == {}
        assert len(caplog.records) == 1
        for record in caplog.records:
            assert record.levelname == "ERROR"
            assert "No such API token" in record.message


def test_paperspace_fail_machine(server, caplog):
    """Should send metrics even if one machine API fails."""
    machines_list = """
      [{"id": "unique_id",
        "name": "Hal 9000",
        "os": "Microsoft Windows Server 2016 Datacenter",
        "ram": "32212246528",
        "cpus": 8,
        "gpu": "Quadro P5000",
        "storageTotal": "268435456000",
        "storageUsed": "70947229184",
        "usageRate": "P5000 hourly",
        "shutdownTimeoutInHours": null,
        "shutdownTimeoutForces": false,
        "performAutoSnapshot": false,
        "autoSnapshotFrequency": null,
        "autoSnapshotSaveCount": null,
        "dynamicPublicIp": false,
        "agentType": "WindowsDesktop",
        "dtCreated": "2019-09-02T17:11:36.374Z",
        "state": "off",
        "updatesPending": false,
        "networkId": "unique_id",
        "privateIpAddress": "x.x.x.x",
        "publicIpAddress": "x.x.x.x",
        "region": "Europe (AMS1)",
        "userId": "unique_id",
        "teamId": "unique_id",
        "scriptId": null,
        "dtLastRun": null}]
    """
    server.add(
        responses.GET,
        "https://api.paperspace.io/machines/getMachines",
        body=machines_list,
        status=200,
    )
    server.add(
        responses.GET,
        "https://api.paperspace.io/machines/getUtilization",
        body='{"error": {"name": "Error", "status": 404, "message": "Machine not found"}}',
        status=404,
    )
    probe = PaperspaceProbe({"api_key": "valid"})
    with caplog.at_level(logging.ERROR):
        probe.run()

        assert len(probe.results) == 5
        assert len(caplog.records) == 1
        for record in caplog.records:
            assert record.levelname == "ERROR"
            assert "Skip machine check" in record.message
