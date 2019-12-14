import logging
import subprocess

from .base import BaseProbe


log = logging.getLogger(__name__)


class WatchdogProbe(BaseProbe):
    """WatchdogProbe Probe detects if a list of hosts are connected to the
    probe network. This probe requires a list of hosts tuples (address, tag-name):
        * [("127.0.0.1", "palazzem")]
        * [("192.168.1.1", "palazzem"), ("test-server", "tali")]

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

        # Dict used to aggregate results instead of extra iterations
        detected_hosts = {}

        for host in self.config["hosts"]:
            # Ping the host to check if present in the network
            address, name = host
            process = subprocess.run(["ping", "-c", "1", address], capture_output=True)
            if process.returncode == 0:
                check = detected_hosts.get(name) or (0, [name])
                detected_hosts[name] = (check[0] + 1, check[1])
            else:
                # Keep debug information with `ping` stdout
                log.debug("Probe watchdog: host '%s' not found", address)

        # Metric: number of detected hosts by tag (name)
        self.results["hal.watchdog.detected_hosts"] = list(detected_hosts.values())
        return True, None
