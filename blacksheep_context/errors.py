from typing import Optional

from blacksheep.messages import Response


class ContextError(BaseException):
    pass


class ContextDoesNotExistError(RuntimeError, ContextError):
    def __init__(self):
        self.message = (
            "You didn't use the required middleware or "
            "you're trying to access `context` object "
            "outside of the request-response cycle."
        )
        super().__init__(self.message)


class ConfigurationError(ContextError):
    pass


class MiddlewareValidationError(ContextError):
    def __init__(self, *args, error_response: Optional[Response] = None) -> None:
        super().__init__(*args)
        self.error_response = error_response
