from os import getenv

from hal.probes.watchdog import WatchdogProbe
from hal.exporters.datadog import DatadogExporter


def entrypoint(event, context):
    """Function entrypoint that uses a WatchdogProbe to see if a list
    of hosts are reachable.

    Environment variables configuration:
      * `DD_API_KEY`: Datadog API key.
      * `DD_HOSTNAME` (default `hal`): Hostname used for the Datadog metric.
      * `WATCHDOG_HOSTS` (default `[]`): List of hostnames or IP addresses to check
      * `WATCHDOG_TAGS` (default `None`): Add tags to all Datadog metrics.

    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    config = {
        "hosts": getenv("WATCHDOG_HOSTS", "").split(),
        "exporters": [
            DatadogExporter(
                {
                    "api_key": getenv("DD_API_KEY"),
                    "hostname": getenv("DD_HOSTNAME", "hal"),
                    "tags": getenv("WATCHDOG_TAGS"),
                }
            )
        ],
    }
    probe = WatchdogProbe(config)
    probe.run()
    probe.export()
