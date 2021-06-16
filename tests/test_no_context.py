import pytest
from blacksheep.contents import JSONContent
from blacksheep.server import Application
from blacksheep.server.responses import json
from blacksheep.testing import TestClient

from blacksheep_context import context


@pytest.fixture(scope="session")
def app():
    app_ = Application()

    @app_.router.post('/ctx')
    def return_context(request):
        # NOTE: context can't be fetched if it not enabled by middleware
        assert context.exists() is False
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
async def test_no_context(client: TestClient):
    response = await client.post(
        '/ctx',
        headers={'X-My-Header-Type': 'My-Special-Value', 'X-My-Header-Type-List': 'AAA'},
        content=JSONContent({'my-info': 1}),
    )

    assert response.status == 500
