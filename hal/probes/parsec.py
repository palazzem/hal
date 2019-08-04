import logging
import requests

from .base import BaseProbe


log = logging.getLogger(__name__)


class ParsecProbe(BaseProbe):
    """Parsec probe collects data from a Parsec API.
    A session ID (access token) is required to authorize the user. The API
    is not officially supported, so the probe may break. A valid session ID can be
    extracted from a browser session, under the `parsec_login` secure cookie.
    """

    DEFAULTS = {
        "session_id": None,
        "url": "https://parsecgaming.com/v1/me",
        "header_key": "X-Parsec-Session-Id",
    }

    def __init__(self, config=None):
        super().__init__(config=config, defaults=ParsecProbe.DEFAULTS)

    def _run(self):
        if not self.config["session_id"]:
            # Missing session ID results in a 403. Bail out.
            return False, "run failed for missing 'session_id'"

        # Call Parsec API to scrape data
        headers = {self.config["header_key"]: self.config["session_id"]}
        response = requests.get(self.config["url"], headers=headers)

        if response.status_code == 200:
            json_resp = response.json()
            self.results = {
                "hal.parsec.play_time": json_resp["play_time"],
                "hal.parsec.credits": json_resp["credits"],
            }
            return True, None
        else:
            return False, "run failed. Server returns '{}'".format(response.text)
