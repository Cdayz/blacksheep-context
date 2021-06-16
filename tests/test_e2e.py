import pytest
from blacksheep.contents import JSONContent
from blacksheep.messages import Request, Response
from blacksheep.server import Application
from blacksheep.server.responses import json
from blacksheep.testing import TestClient

from blacksheep_context import context
from blacksheep_context.middleware import ContextMiddleware
from blacksheep_context.plugins import BasePlugin, HeaderPlugin


@pytest.fixture(scope="session")
def app():

    class MyHeaderPlugin(HeaderPlugin):
        header_key = b'X-My-Header-Type'
        context_key = 'my_header_type'
        single_value_header = True

    class MyListHeaderPlugin(HeaderPlugin):
        header_key = b'X-My-Header-Type-List'
        context_key = 'my_list_header_type'
        single_value_header = False

    class MyNonExistentHeaderPlugin(HeaderPlugin):
        header_key = b'X-No-Header'
        context_key = 'my_no_header'
        single_value_header = False

    class MyCustomPlugin(BasePlugin):
        context_key = 'user-data'

        async def process_request(self, request: Request):
            try:
                data = await request.json()
                return data.get('user-id')
            except Exception:
                return None

        async def enrich_response(self, response: Response) -> None:
            response.add_header(b'X-My-Out-Header-Type', context['my_header_type'].encode('utf-8'))

    ctx_middleware = ContextMiddleware(
        plugins=[
            MyHeaderPlugin(),
            MyListHeaderPlugin(),
            MyNonExistentHeaderPlugin(),
            MyCustomPlugin(),
        ],
    )

    app_ = Application()
    app_.middlewares.append(ctx_middleware)

    @app_.router.post('/ctx')
    def return_context(request):
        assert context.exists()
        return json(context.copy())

    return app_


@pytest.fixture
@pytest.mark.asyncio
async def client(app: Application):
    await app.start()
    try:
        yield TestClient(app)
    finally:
        await app.stop()


@pytest.mark.asyncio
async def test_context_fetched(client: TestClient):
    response = await client.post(
        '/ctx',
        headers={'X-My-Header-Type': 'My-Special-Value', 'X-My-Header-Type-List': 'AAA'},
        content=JSONContent({'my-info': 1}),
    )

    data = await response.json()

    # Context can be fetched in view function
    assert data == {
        'my_header_type': 'My-Special-Value',
        'user-data': None,
        'my_list_header_type': ['AAA'],
        'my_no_header': None,
    }

    # Context can be used in middlewares too
    assert response.headers.contains(b'X-My-Out-Header-Type')
    assert response.get_first_header(b'X-My-Out-Header-Type') == b'My-Special-Value'


@pytest.mark.asyncio
async def test_context_fetched_fully(client: TestClient):
    response = await client.post(
        '/ctx',
        headers={'X-My-Header-Type': 'My-Special-Value', 'X-My-Header-Type-List': 'AAA'},
        content=JSONContent({'my-info': 1, 'user-id': 12}),
    )

    data = await response.json()

    # Context can be fetched in view function
    assert data == {
        'my_header_type': 'My-Special-Value',
        'user-data': 12,
        'my_list_header_type': ['AAA'],
        'my_no_header': None,
    }

    # Context can be used in middlewares too
    assert response.headers.contains(b'X-My-Out-Header-Type')
    assert response.get_first_header(b'X-My-Out-Header-Type') == b'My-Special-Value'
