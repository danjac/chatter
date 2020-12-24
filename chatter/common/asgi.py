# Django
from django.conf import settings

# Third Party Libraries
from channels.middleware import BaseMiddleware


class CORSWrapper:
    def __init__(self, send):
        self.real_send = send

    async def send(self, message):
        message["headers"] = message.get("headers", []) + self.cors_headers()
        print("send headers....", message["headers"])
        await self.real_send(message)

    def cors_headers(self):

        headers = []
        cors_origin = ""
        if hasattr(settings, "EVENTSTREAM_ALLOW_ORIGIN"):
            cors_origin = settings.EVENTSTREAM_ALLOW_ORIGIN

        if cors_origin:
            headers.append(
                (b"Access-Control-Allow-Origin", bytes(cors_origin, encoding="utf-8"))
            )

        allow_credentials = False
        if hasattr(settings, "EVENTSTREAM_ALLOW_CREDENTIALS"):
            allow_credentials = settings.EVENTSTREAM_ALLOW_CREDENTIALS

        if allow_credentials:
            headers.append((b"Access-Control-Allow-Credentials", b"true"))
        return headers


class CORSMiddleware(BaseMiddleware):
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        await self.inner(scope, receive, CORSWrapper(send).send)
