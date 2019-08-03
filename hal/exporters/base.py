class BaseExporter(object):
    """BaseExporter defines the interface to send probe data to an external system."""

    DEFAULTS = {}

    def __init__(self, config=None):
        config = config or {}
        self.config = {**BaseExporter.DEFAULTS, **config}

    def send(self, data):
        """Send must be implemented in the child class to define how data is serialized
        and exported to another system.

        Args:
            data: Probe data that should be sent to an external system.
        Raises:
            NotImplementedError: This class is not supposed to be used directly.
        """
        raise NotImplementedError()
