import datadog
import logging

from .base import BaseExporter


log = logging.getLogger(__name__)


class DatadogExporter(BaseExporter):
    """DatadogExporter sends data to Datadog API. Every kwarg in the results dictionary
    is used as a metric name, so the naming of your keys is important. As example, if
    the result dictionary is ``{"hal.metric": 42}`` the exporter sends a metric
    named ``hal.metric``.

    If the metric has custom tags, it's possible to use a tuble as a dict value:
    ``{"hal.metric": (42, ["tag_1"])}``. In that case, the metric ``hal.metric`` has
    ``42`` as data point and ``tag_1`` as tag. In case ``tags`` in the exporter configuration
    is set, the lists are merged.
    """

    DEFAULTS = {"api_key": None, "hostname": None, "tags": None}

    def __init__(self, config=None):
        super().__init__(config)
        datadog.initialize(
            api_key=self.config["api_key"], host_name=self.config["hostname"]
        )

    def send(self, data):
        # Validate configuration
        if self.config["api_key"] is None:
            log.error("DatadogExporter: api_key is not configured.")
            return

        if self.config["tags"] is not None and not isinstance(
            self.config["tags"], list
        ):
            log.error("DatadogExporter: 'tags' must be a list of strings.")
            return

        for k, v in data.items():
            # Convert the metric data points in a list of metrics
            # to allow sending multiple metrics with the same name
            if not isinstance(v, list):
                v = [v]

            for metric in v:
                # For each metric, detect if multiple tags are available
                if isinstance(metric, tuple):
                    points = metric[0]
                    tags = (self.config["tags"] or []) + metric[1]
                else:
                    points = metric
                    tags = self.config["tags"]

                # NOTE: Hostname is automatically attached from config
                response = datadog.api.Metric.send(tags=tags, metric=k, points=points)
                if response.get("status") != "ok":
                    log.error(
                        "DatadogExporter: unable to send metric. Server response was '%s'",
                        response,
                    )
                else:
                    log.info("DatadogExporter: metric '%s' sent correctly", k)
