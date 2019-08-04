import datadog
import logging

from .base import BaseExporter


log = logging.getLogger(__name__)


class DatadogExporter(BaseExporter):
    """DatadogExporter sends data to Datadog API. Every kwarg in the results dictionary
    is used as a metric name, so the naming of your keys is important. As example, if
    the result dictionary is ``{"hal.metric": 42}`` the exporter sends a metric
    named ``hal.metric``.
    """

    DEFAULTS = {"api_key": None, "hostname": None, "tags": None}

    def __init__(self, config=None):
        super().__init__(config)
        datadog.initialize(api_key=self.config["api_key"])

    def send(self, data):
        if self.config["api_key"] is None:
            log.error("DatadogExporter: api_key is not configured.")
            return

        for k, v in data.items():
            response = datadog.api.Metric.send(
                host=self.config["hostname"],
                tags=self.config["tags"],
                metric=k,
                points=v,
            )

            if response.get("status") != "ok":
                log.error(
                    "DatadogExporter: unable to send metric. Server response was '%s'",
                    response,
                )
            else:
                log.info("DatadogExporter: metric '%s' sent correctly", k)
