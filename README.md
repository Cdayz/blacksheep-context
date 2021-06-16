# Blacksheep Context

[![Build Status](https://github.com/Cdayz/blacksheep-context/workflows/Continuous%20Integration/badge.svg)](https://github.com/Cdayz/blacksheep-context/actions)
[![codecov](https://codecov.io/gh/Cdayz/blacksheep-context/branch/master/graph/badge.svg?token=5KFIGS17S4)](https://codecov.io/gh/Cdayz/blacksheep-context)
[![Package Version](https://img.shields.io/pypi/v/blacksheep-context?logo=PyPI&logoColor=white)](https://pypi.org/project/blacksheep-context/)
[![PyPI Version](https://img.shields.io/pypi/pyversions/blacksheep-context?logo=Python&logoColor=white)](https://pypi.org/project/blacksheep-context/)

## Introduction

Middleware for Blacksheep that allows you to store and access the context data of a request.
Can be used with logging so logs automatically use request headers such as x-request-id or x-correlation-id.

## Requirements

* Python 3.7+
* Blacksheep 1.0.7+

## Installation

```console
$ pip install blacksheep-context
```

## Usage

A complete example shown below.

```python
from blacksheep.server import Application
from blacksheep.messages import Request, Response
from blacksheep.server.responses import json

from blacksheep_context import context
from blacksheep_context.middleware import ContextMiddleware
from blacksheep_context.plugins import BasePlugin, HeaderPlugin


class RequestIdPlugin(HeaderPlugin):
    header_key = b'X-Request-Id'
    # Every plugin must provide this attribute
    context_key = 'request-id'
    # Fetches only first value of header, can be False to insert all values of header into context
    single_value_header = True

    # Also allow you to add some data from context into response
    async def enrich_response(self, response: Response) -> None:
        response.add_header(b'X-Request-Id', context['request_id'].encode('utf-8'))


class MyCustomPlugin(BasePlugin):
    context_key = 'user-data'

    # You can customize fetching data from request
    async def process_request(self, request: Request):
        try:
            data = await request.json()
            return data.get('user-id')
        except Exception:
            return None


ctx_middleware = ContextMiddleware(plugins=[RequestIdPlugin(), MyCustomPlugin()])

app_ = Application()
app_.middlewares.append(ctx_middleware)

@app_.router.post('/ctx')
def return_context(request):
    assert context.exists() is True
    return json(context.copy())
```

## Contributing

This project is absolutely open to contributions so if you have a nice idea, create an issue to let the community 
discuss it.
