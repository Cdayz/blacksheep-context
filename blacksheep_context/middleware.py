from contextvars import Token
from typing import Awaitable, Callable, Optional, Sequence

from blacksheep.messages import Request, Response

from blacksheep_context import _request_scope_context_storage
from blacksheep_context.errors import ConfigurationError, MiddlewareValidationError
from blacksheep_context.plugins.base import BasePlugin


class ContextMiddleware:
    def __init__(
        self,
        plugins: Optional[Sequence[BasePlugin]] = None,
        defaut_error_response: Response = Response(status=400),
        *args,
        **kwargs,
    ) -> None:
        for plugin in plugins or ():
            if not isinstance(plugin, BasePlugin):
                raise ConfigurationError(f"Plugin {plugin} is not a valid instance")
        self.plugins = plugins or ()
        self.error_response = defaut_error_response

    async def set_context(self, request: Request) -> dict:
        return {
            plugin.context_key: await plugin.process_request(request)
            for plugin in self.plugins
        }

    async def __call__(self, request: Request, handler: Callable[[Request], Awaitable[Response]]) -> Response:
        try:
            context = await self.set_context(request)
            token: Token = _request_scope_context_storage.set(context)
        except MiddlewareValidationError as e:
            if e.error_response:
                error_response = e.error_response
            else:
                error_response = self.error_response
            return error_response

        try:
            response = await handler(request)
            for plugin in self.plugins:
                await plugin.enrich_response(response)

        finally:
            _request_scope_context_storage.reset(token)

        return response
