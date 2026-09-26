class DatabpyError(Exception):
    """Base class for all errors raised by databpy."""


class LinkedObjectError(DatabpyError):
    """
    Error raised when a Python object doesn't have a linked object in the 3D scene.

    Parameters
    ----------
    message : str
        The error message describing why the linked object is missing or invalid.

    Attributes
    ----------
    message : str
        The error message that was passed.
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
