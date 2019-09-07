from os import getenv

from hal.probes.paperspace import PaperspaceProbe
from hal.exporters.datadog import DatadogExporter


def entrypoint(event, context):
    """Cloud Function entrypoint to retrieve data from Paperspace API.

    Environment variables configuration:
      * `DD_API_KEY`: Datadog API key.
      * `DD_HOSTNAME` (default `hal`): Hostname used for the Datadog metric.
      * `PAPERSPACE_TAGS` (default `None`): Add tags to all Datadog metrics.
      * `PAPERSPACE_API_KEY`: API key used to authenticate API calls.

    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    config = {
        "api_key": getenv("PAPERSPACE_API_KEY"),
        "exporters": [
            DatadogExporter(
                {
                    "api_key": getenv("DD_API_KEY"),
                    "hostname": getenv("DD_HOSTNAME", "hal"),
                    "tags": getenv("PAPERSPACE_TAGS"),
                }
            )
        ],
    }
    probe = PaperspaceProbe(config)
    probe.run()
    probe.export()
