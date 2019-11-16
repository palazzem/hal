import logging
import subprocess

from .base import BaseProbe


log = logging.getLogger(__name__)


class WatchdogProbe(BaseProbe):
    """WatchdogProbe Probe detects if a list of hosts are connected to the
    probe network. This probe requires a list of hosts address:
        * ["127.0.0.1"]
        * ["192.168.1.1", "test-server"]

    Under the hood, `WatchdogProbe` uses `ping` sending a single packet and
    checking the return code. `subprocess` is used
    The Probe collects the following metrics:
        * Number of connected hosts from the given list
    """

    DEFAULTS = {
        "hosts": [],
    }

    def _run(self):
        if not self.config["hosts"]:
            # Bail out if hosts are not defined
            return False, "run failed for missing hosts to monitor"

        # Metric: number of detected hosts
        self.results["hal.watchdog.detected_hosts"] = 0

        for host in self.config["hosts"]:
            # Ping the host to check if present in the network
            process = subprocess.run(["ping", "-c", "1", host], capture_output=True)
            if process.returncode == 0:
                self.results["hal.watchdog.detected_hosts"] += 1
            else:
                # Keep debug information with `ping` stdout
                log.debug("Probe watchdog: host '%s' not found", host)

        return True, None
