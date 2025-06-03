import json
from channels.generic.websocket import AsyncWebsocketConsumer
from urllib.parse import parse_qs


class RealtimeConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # JWT authentication for WebSocket connections
        from rest_framework_simplejwt.tokens import UntypedToken
        from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
        from django.db import close_old_connections
        from jwt import decode as jwt_decode
        from django.conf import settings

        self.user = None
        try:
            query_string = self.scope["query_string"].decode()
            token = parse_qs(query_string).get("token")
            if token:
                token = token[0]
                UntypedToken(token)
                decoded_data = jwt_decode(
                    token, settings.SECRET_KEY, algorithms=["HS256"]
                )
                user_id = decoded_data.get("user_id")
                self.user = await self.get_user(user_id)
                close_old_connections()
        except (InvalidToken, TokenError, Exception):
            await self.close()
            return
        if not self.user:
            await self.close()
            return

        # Subscribe to a group for this user (or topic)
        self.group_name = f"user_{self.user.id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    @staticmethod
    async def get_user(user_id):
        from django.contrib.auth import get_user_model

        User = get_user_model()
        try:
            return await User.objects.aget(id=user_id)
        except User.DoesNotExist:
            return None

    async def disconnect(self, code):
        group_name = getattr(self, "group_name", None)
        if group_name:
            await self.channel_layer.group_discard(group_name, self.channel_name)

    async def receive(self, text_data):
        # Optionally handle messages from frontend
        pass

    async def send_realtime_event(self, event):
        # Called by backend to send data to frontend
        await self.send(text_data=json.dumps(event["data"]))
