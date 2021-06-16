import abc
from typing import Any, Optional

from blacksheep.messages import Request, Response


class BasePlugin(metaclass=abc.ABCMeta):
    context_key: str

    @abc.abstractmethod
    async def process_request(self, request: Request) -> Optional[Any]:
        pass

    @abc.abstractmethod
    async def enrich_response(self, arg: Response) -> None:
        pass
