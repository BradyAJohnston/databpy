class DatabpyError(Exception):
    """Base class for all errors raised by databpy."""


class LinkedObjectError(DatabpyError):
    """
    Error raised when a wrapper can no longer find the Blender object it is linked to.

    Raised when the object of a `BlenderObject` or `AttributeArray` has been removed,
    or an `AttributeArray` is synced after a file was loaded.

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
