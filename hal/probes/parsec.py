import logging
import requests

from .base import BaseProbe


log = logging.getLogger(__name__)


class ParsecProbe(BaseProbe):
    """TODO"""

    DEFAULTS = {
        "session_id": None,
        "url": "https://parsecgaming.com/v1/me",
        "header_key": "X-Parsec-Session-Id",
    }

    def __init__(self, config=None):
        super().__init__(config=config, defaults=ParsecProbe.DEFAULTS)

    def run(self):
        if self.config["session_id"] is None:
            # Missing session ID results in a 401. Bail out.
            log.error("ParsecProbe: run failed for missing 'session_id'")
            return False

        # Call Parsec API to scrape data
        headers = {self.config["header_key"]: self.config["session_id"]}
        response = requests.get(self.config["url"], headers=headers)

        if response.status_code == 200:
            json_resp = response.json()
            self.results = {
                "play_time": json_resp["play_time"],
                "credits": json_resp["credits"],
            }
            return True
        else:
            log.error("ParsecProbe: run failed. Server returns '%s'", response.text)
            return False
