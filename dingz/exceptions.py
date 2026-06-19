"""Exceptions for dingz API client."""


class DingzError(Exception):
    """General dingz exception occurred."""


class DingzConnectionError(DingzError):
    """When a connection error is encountered."""


class DingzNoDataAvailable(DingzError):
    """When no data is available."""
