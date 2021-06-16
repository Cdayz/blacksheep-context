import pytest
from blacksheep.contents import Content
from blacksheep.messages import Request, Response
from blacksheep.server import Application
from blacksheep.server.responses import text
from blacksheep.testing import TestClient

from blacksheep_context.errors import ConfigurationError, MiddlewareValidationError
from blacksheep_context.middleware import ContextMiddleware
from blacksheep_context.plugins import BasePlugin


@pytest.fixture(scope="session")
def app():
    class FailingPlugin(BasePlugin):
        context_key = 'user-data'

        async def process_request(self, request: Request):
            if not request.declares_json():
                raise MiddlewareValidationError(error_response=Response(status=407))

            raise MiddlewareValidationError()

        async def enrich_response(self, arg: Response) -> None:
            pass

    ctx_middleware = ContextMiddleware(plugins=[FailingPlugin()])

    app_ = Application()
    app_.middlewares.append(ctx_middleware)

    @app_.router.post('/ctx')
    def return_context(request):
        return text('ok')

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
async def test_error_from_plugin(client: TestClient):
    response = await client.post(
        '/ctx',
        content=Content(content_type=b'application/text', data=b'my-data'),
    )

    assert response.status == 407


@pytest.mark.asyncio
async def test_error_from_middleware(client: TestClient):
    response = await client.post(
        '/ctx',
        content=Content(content_type=b'application/json', data=b'my-data'),
    )

    assert response.status == 400


def test_middleware_construction():
    with pytest.raises(ConfigurationError):
        ContextMiddleware(plugins=['broken'])
