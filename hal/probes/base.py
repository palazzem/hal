import logging


log = logging.getLogger(__name__)


class BaseProbe(object):
    """Defines a base `Probe` that collects data from an internal/external service.
    This class must be extended and the following methods must be implemented:
      * ``_run()``: this function is called to execute the probe and must contain the
        probe logic.

    The public API includes:
      * ``run()``: use this to launch the probe logic.
      * ``export()``: send data stored in the probe to another system.

    Exporters can be defined by overriding the `exporters` key in the config object.
    The setting must be a list of callables.

    Usage:
        # Initialize the probe with extra config
        config = {"exporters": [Exporter1(), Exportert2()]}
        probe = BaseProbe(config)

        # Run the probe and check for results
        probe.run()
        probe.results

        # Export the results based on configured exporter
        probe.export()
    """

    DEFAULTS = {}
    BASE_DEFAULTS = {"exporters": []}

    def __init__(self, config=None):
        config = config or {}
        self.config = {**BaseProbe.BASE_DEFAULTS, **self.DEFAULTS, **config}
        self.results = None

    def _run(self):
        """Defines the probe logic. This method must be implemented in the child class, and probe
        results must be stored in ``self.results``.

        Raises:
            NotImplementedError: the class must be extended to be used.
        """
        raise NotImplementedError()

    def run(self):
        """Probe public API that must be called by the main program. It differs from `_run()`
        because this must not be implemented in child classes, and is used only to share
        a common logic between probes.

        Returns:
            A boolean that represents the success or failure of the data collection.
        """
        log.debug("%s: started", self.__class__.__name__)
        status, msg = self._run()
        if status:
            log.info("%s: completed with success", self.__class__.__name__)
        else:
            log.error("%s: %s", self.__class__.__name__, msg)
        return status

    def export(self):
        """Exports results stored in ``self.results`` somewhere. The export mechanism is defined
        in the probe configuration as "exporter" key and this function is also delegated to
        define the export format, and the platform (database, console, third party service, etc...)
        where probe data is sent.
        """
        if not self.results:
            log.warning(
                "%s: export() executed with no results available",
                self.__class__.__name__,
            )
            return

        try:
            for exporter in self.config["exporters"]:
                exporter.send(self.results)
        except TypeError:
            log.error(
                "%s: some exporters are not valid; execution aborted",
                self.__class__.__name__,
            )
