import logging
import requests

from datetime import datetime
from .base import BaseProbe


log = logging.getLogger(__name__)


class PaperspaceProbe(BaseProbe):
    """Paperspace Probe collects data from Paperspace REST API.
    This probe requires a valid API key that you can create in your Paperspace
    account: https://www.paperspace.com/console/account/api
    The Probe collects the following metrics:
        * Number of available instances
        * State of all registered instances
        * Usage (in seconds) for all instances
        * Hourly rate for all instances
        * Monthly rate for attached storages

    To retrieve billing metrics, the current time (``now()``) is used.
    """

    DEFAULTS = {
        "api_key": None,
        "base_url": "https://api.paperspace.io",
        "header_key": "x-api-key",
    }

    def _run(self):
        if not self.config["api_key"]:
            # Bail out if the Paperspace API key is missing
            return False, "run failed for missing Paperspace API key"

        # Billing date for the current month (format: 2019-09)
        billing_period = datetime.now().strftime("%Y-%m")

        # Use Paperspace API key for authentication
        headers = {self.config["header_key"]: self.config["api_key"]}

        # List information about all machines available
        url = "{}/{}".format(self.config["base_url"], "machines/getMachines")
        response = requests.get(url, headers=headers)

        # Bail out if we cannot retrieve the list of machines
        if response.status_code != 200:
            return False, "run failed. Server returns '{}'".format(response.text)
        machines = response.json()

        # Metric: number of registered machines
        self.results["hal.paperspace.machines.count"] = len(machines)
        self.results["hal.paperspace.machines.instance"] = []

        for machine in machines:
            # Metric: state of the instance (off/ready)
            is_off = int(machine["state"] == "off")
            is_ready = int(machine["state"] == "ready")
            self.results["hal.paperspace.machines.instance"].append(
                (is_off, ["machine_id:{}".format(machine["id"]), "state:off"])
            )
            self.results["hal.paperspace.machines.instance"].append(
                (is_ready, ["machine_id:{}".format(machine["id"]), "state:ready"])
            )
            # Metric: report other temporary state
            if not is_off and not is_ready:
                self.results["hal.paperspace.machines.instance"].append(
                    (
                        1,
                        [
                            "machine_id:{}".format(machine["id"]),
                            "state:{}".format(machine["state"]),
                        ],
                    )
                )

            # Get machine utilization data for the machine with the given ID
            url = "{}/{}".format(self.config["base_url"], "machines/getUtilization")
            params = {"machineId": machine["id"], "billingMonth": billing_period}
            response = requests.get(url, headers=headers, params=params)

            # Skip the rest but log the error
            if response.status_code != 200:
                log.error(
                    "Skip machine check. Server returns '{}'".format(response.text)
                )
                continue

            billing = response.json()
            # Metric: usage (in seconds) for the given machine
            self.results["hal.paperspace.utilization.instance.usage_seconds"] = (
                int(billing["utilization"]["secondsUsed"]),
                ["machine_id:{}".format(machine["id"])],
            )

            # Metric: hourly rate for the given machine
            self.results["hal.paperspace.utilization.instance.hourly_rate"] = (
                float(billing["utilization"]["hourlyRate"]),
                ["machine_id:{}".format(machine["id"])],
            )

            # Metric: monthly rate for the attached storage
            self.results["hal.paperspace.utilization.storage.monthly_rate"] = (
                float(billing["storageUtilization"]["monthlyRate"]),
                ["machine_id:{}".format(machine["id"])],
            )

        return True, None
