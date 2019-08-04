from os import getenv

from hal.probes.parsec import ParsecProbe
from hal.exporters.datadog import DatadogExporter


def entrypoint():
    """Cloud Function entrypoint to retrieve data from Parsec Gaming.

    Environment variables configuration:
      * `DD_API_KEY`: Datadog API key.
      * `DD_HOSTNAME` (default `hal`): Hostname used for the Datadog metric.
      * `PARSEC_TAGS` (default `None`): Add tags to Datadog metrics.
      * `PARSEC_TOKEN`: Token extracted from a browser session.
    """
    config = {
        "session_id": getenv("PARSEC_TOKEN"),
        "exporters": [
            DatadogExporter(
                {
                    "api_key": getenv("DD_API_KEY"),
                    "hostname": getenv("DD_HOSTNAME", "hal"),
                    "tags": getenv("PARSEC_TAGS"),
                }
            )
        ],
    }
    probe = ParsecProbe(config)
    probe.run()
    probe.export()
