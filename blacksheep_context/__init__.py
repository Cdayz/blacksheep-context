from contextvars import ContextVar
from typing import Any, Dict

_request_scope_context_storage: ContextVar[Dict[Any, Any]] = ContextVar("blacksheep_context")

from .ctx import context  # noqa: F401, E402
