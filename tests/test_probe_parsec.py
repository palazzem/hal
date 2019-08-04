import logging
import responses

from hal.probes.parsec import ParsecProbe


def test_parsec_probe():
    """Should be initialized with a default config."""
    probe = ParsecProbe()
    assert probe.config["session_id"] is None
    assert probe.config["url"] is not None
    assert probe.config["header_key"] is not None


def test_parsec_run_without_session(caplog):
    """Should fail if a session ID is not set."""
    probe = ParsecProbe()
    with caplog.at_level(logging.ERROR):
        result = probe.run()

        assert len(caplog.records) == 1
        for record in caplog.records:
            assert record.levelname == "ERROR"
            assert "missing 'session_id'" in record.message
            assert result is False


def test_parsec_success(server):
    """Should succeed with a valid session ID."""
    html = """
      {"friend_permissions": {
        "control": 0,
        "add_controller": 1,
        "control_keyboard": 0,
        "control_mouse": 0,
        "connect": 0,
        "connect_init": 1,
        "type": "PermissionType.Friend"
      },
      "num_cards": 1,
      "party_invites": [],
      "account_status": null,
      "id": 2,
      "staff": false,
      "is_confirmed": true,
      "has_card": true,
      "default_avatar_url": "https://s3.amazonaws.com/parseccloud/thumb/8.jpg",
      "pending_friend_requests": [],
      "play_time": 5000,
      "email": "hello@palazzetti.me",
      "waitlist": {},
      "warp": false,
      "updated_at": "2019-07-29T15:06:27",
      "credits": 100,
      "name": "palazzem",
      "created_at": "2019-05-05T12:55:06",
      "avatar_url": "https://public.parsecgaming.com/user-data/ultros/1148435/avatar",
      "flags": {},
      "avatar": null,
      "sent_friend_requests": []}
    """
    server.add(responses.GET, "https://parsecgaming.com/v1/me", body=html, status=200)
    probe = ParsecProbe({"session_id": "valid"})
    probe.run()
    assert len(probe.results) == 2
    assert probe.results["hal.parsec.play_time"] == 5000
    assert probe.results["hal.parsec.credits"] == 100


def test_parsec_fail(server, caplog):
    """Should fail if an invalid session ID is used."""
    server.add(
        responses.GET,
        "https://parsecgaming.com/v1/me",
        body="Session invalid.",
        status=403,
    )
    probe = ParsecProbe({"session_id": "invalid"})
    with caplog.at_level(logging.ERROR):
        probe.run()

        assert probe.results is None
        assert len(caplog.records) == 1
        for record in caplog.records:
            assert record.levelname == "ERROR"
            assert "Server returns 'Session invalid.'" in record.message
