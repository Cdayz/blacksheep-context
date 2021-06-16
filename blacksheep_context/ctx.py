import copy
from collections import UserDict
from contextvars import copy_context
from typing import Any

from blacksheep_context import _request_scope_context_storage
from blacksheep_context.errors import ConfigurationError, ContextDoesNotExistError


class _Context(UserDict):
    def __init__(self, *args: Any, **kwargs: Any):  # noqa
        # not calling super on purpose
        if args or kwargs:
            raise ConfigurationError("Can't instantiate with attributes")

    @property
    def data(self) -> dict:
        try:
            return _request_scope_context_storage.get()
        except LookupError:
            raise ContextDoesNotExistError

    def exists(self) -> bool:
        return _request_scope_context_storage in copy_context()

    def copy(self) -> dict:
        return copy.copy(self.data)


context = _Context()
