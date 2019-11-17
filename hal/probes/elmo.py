import logging

from elmo.api.client import ElmoClient
from requests.exceptions import HTTPError

from .base import BaseProbe


log = logging.getLogger(__name__)


class ElmoProbe(BaseProbe):
    """TODO
    """

    DEFAULTS = {
        "base_url": None,
        "vendor": None,
        "username": None,
        "password": None,
    }

    def _run(self):
        if not self.config["base_url"] or not self.config["vendor"]:
            # Bail out if the Elmo endpoint is not defined
            return False, "run failed for missing 'base_url' and 'vendor' endpoint"

        if not self.config["username"] or not self.config["password"]:
            # Bail out if credentials are not defined
            return False, "run failed for missing credentials"

        # Access Elmo and get the system status
        try:
            client = ElmoClient(self.config["base_url"], self.config["vendor"])
            client.auth(self.config["username"], self.config["password"])
            status = client.check()
        except HTTPError as e:
            return False, "run failed. ElmoClient returns '{}'".format(e)

        # Metrics: collect armed/disarmed areas and system inputs status
        self.results["hal.elmo.areas"] = []
        self.results["hal.elmo.inputs"] = []

        # Collect metrics
        for item in status["areas_armed"]:
            self.results["hal.elmo.areas"].append(
                (1, ["name:{}".format(item["name"]), "status:armed"])
            )
        for item in status["areas_disarmed"]:
            self.results["hal.elmo.areas"].append(
                (1, ["name:{}".format(item["name"]), "status:disarmed"])
            )
        for item in status["inputs_alerted"]:
            self.results["hal.elmo.inputs"].append(
                (1, ["name:{}".format(item["name"]), "status:alerted"])
            )
        for item in status["inputs_wait"]:
            self.results["hal.elmo.inputs"].append(
                (1, ["name:{}".format(item["name"]), "status:wait"])
            )

        return True, None
