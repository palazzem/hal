import logging


log = logging.getLogger(__name__)


class BaseProbe(object):
    """Defines a base `Probe` that collects data from an internal/external service.
    This class must be extended and the following methods must be implemented:
      * ``run()``: this function is called to execute the probe and must contain the
        probe logic.

    An ``export()`` method is available to export results stored in the probe. To define
    an exporter, override the "exporter" key in the config object. The exporter must be
    a callable.

    Usage:
        # Initialize the probe with extra config
        config = {"poll_interval": 5}
        probe = BaseProbe(config)

        # Run the probe and check for results
        probe.run()
        probe.results

        # Export the results based on configured exporter
        probe.export()
    """

    BASE_DEFAULTS = {"exporters": []}

    def __init__(self, config=None, defaults=None):
        config = config or {}
        defaults = defaults or {}
        self.config = {**BaseProbe.BASE_DEFAULTS, **defaults, **config}
        self.results = None

    def run(self):
        """Defines the probe logic. This method must be implemented in the child class, and probe
        results must be stored in ``self.results``.

        Raises:
            NotImplementedError: the class must be extended to be used.
        """
        raise NotImplementedError()

    def export(self):
        """Exports results stored in ``self.results`` somewhere. The export mechanism is defined
        in the probe configuration as "exporter" key and this function is also delegated to
        define the export format, and the platform (database, console, third party service, etc...)
        where probe data is sent.
        """
        if self.results is None or self.results == "":
            log.warning("export() executed but no results are available in the probe.")

        try:
            for exporter in self.config["exporters"]:
                exporter.send(self.results)
        except TypeError:
            log.error("Exporter not available for this probe.")
