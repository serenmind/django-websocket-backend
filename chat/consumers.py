import json
from channels.generic.websocket import AsyncWebsocketConsumer
from urllib.parse import parse_qs


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Import Django/DRF only when needed
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
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
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
        # Safely handle disconnect even if room_group_name was never set
        room_group_name = getattr(self, "room_group_name", None)
        channel_layer = getattr(self, "channel_layer", None)
        if room_group_name and channel_layer:
            await channel_layer.group_discard(room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data["message"]
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "user": self.user.username if self.user else "Anonymous",
            },
        )

    async def chat_message(self, event):
        message = event["message"]
        user = event.get("user", "Anonymous")
        await self.send(text_data=json.dumps({"user": user, "message": message}))
