class NameAlreadyExistsError(Exception):
    """Raised when a given name already exists."""

    pass


class ResourceExistsError(Exception):
    """Raised when a resource already exists."""

    pass


class ResourceInUseError(Exception):
    """Raised when a resource is still referenced by a batch and cannot be deleted."""

    pass
