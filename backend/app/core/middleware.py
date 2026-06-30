"""Custom ASGI middleware.

Adds a unique request identifier to every response so that individual API
calls can be correlated across logs for auditing — a requirement for a
fintech system.
"""

import uuid
from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

REQUEST_ID_HEADER = "X-Request-ID"


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Attach a unique ``X-Request-ID`` header to each response.

    If the client supplies its own request id it is preserved; otherwise a new
    UUID4 is generated. The id is also stored on ``request.state`` so handlers
    and loggers can reference it.
    """

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Generate/propagate the request id and set it on the response."""
        request_id = request.headers.get(REQUEST_ID_HEADER) or str(uuid.uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers[REQUEST_ID_HEADER] = request_id
        return response
