from typing import Any, Optional

from blacksheep.messages import Request, Response

from blacksheep_context.plugins.base import BasePlugin


class HeaderPlugin(BasePlugin):
    header_key: bytes
    single_value_header: bool = False

    async def extract_value_from_header_by_key(self, request: Request) -> Optional[str]:
        header_values = request.headers.get(self.header_key)

        if not header_values:
            return None

        if self.single_value_header:
            return header_values[0].decode('utf-8')

        return [h.decode('utf-8') for h in header_values]

    async def process_request(self, request: Request) -> Optional[Any]:
        assert isinstance(self.header_key, bytes)
        return await self.extract_value_from_header_by_key(request)

    async def enrich_response(self, arg: Response) -> None:
        pass
