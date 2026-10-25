"""Request context and bounded request-body handling."""

import logging
from uuid import uuid4

from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

logger = logging.getLogger(__name__)


class RequestContextMiddleware:
    """Buffer bounded request bodies and attach a safe request identifier."""

    def __init__(self, app: ASGIApp, max_body_bytes: int) -> None:
        self.app = app
        self.max_body_bytes = max_body_bytes

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = dict(scope.get("headers", []))
        incoming_id = headers.get(b"x-request-id", b"")
        request_id = (
            incoming_id.decode("ascii")
            if 0 < len(incoming_id) <= 128 and all(32 <= char <= 126 for char in incoming_id)
            else str(uuid4())
        )
        body = bytearray()
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            body.extend(message.get("body", b""))
            if len(body) > self.max_body_bytes:
                response = JSONResponse(
                    status_code=413,
                    content={
                        "error": {
                            "code": "request_too_large",
                            "message": "Request body exceeds the configured size limit.",
                            "details": {},
                        }
                    },
                )
                await response(scope, receive, self._send_with_id(send, request_id))
                logger.info(
                    "request_id=%s method=%s path=%s status=413",
                    request_id,
                    scope["method"],
                    scope["path"],
                )
                return
            if not message.get("more_body", False):
                break

        body_sent = False

        async def replay_receive() -> Message:
            nonlocal body_sent
            if body_sent:
                return {"type": "http.request", "body": b"", "more_body": False}
            body_sent = True
            return {"type": "http.request", "body": bytes(body), "more_body": False}

        status_code = 500

        async def send_with_status(message: Message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await self._send_with_id(send, request_id)(message)

        try:
            await self.app(scope, replay_receive, send_with_status)
        finally:
            logger.info(
                "request_id=%s method=%s path=%s status=%s",
                request_id,
                scope["method"],
                scope["path"],
                status_code,
            )

    @staticmethod
    def _send_with_id(send: Send, request_id: str):
        async def send_response(message: Message) -> None:
            if message["type"] == "http.response.start":
                response_headers = list(message.get("headers", []))
                response_headers.append((b"x-request-id", request_id.encode("ascii")))
                message["headers"] = response_headers
            await send(message)

        return send_response
