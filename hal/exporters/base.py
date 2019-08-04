class BaseExporter(object):
    """BaseExporter defines the interface to send probe data to an external system.
    This class must be implemented by overriding the following methods:
      * ``send()``: defines what is sent to the external service.
    """

    DEFAULTS = {}

    def __init__(self, config=None):
        config = config or {}
        self.config = {**self.DEFAULTS, **config}

    def send(self, data):
        """Send must be implemented in the child class to define how data is serialized
        and exported to another system.

        Args:
            data: Probe data that should be sent to an external system.
        Raises:
            NotImplementedError: This class is not supposed to be used directly.
        """
        raise NotImplementedError()
