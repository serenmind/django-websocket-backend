from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def notify_user(user_id, data):
    """
    How to Use
    The frontend connects to /ws/realtime/?token=<jwt>.
    The backend (any app) calls notify_user() to push real-time data.
    The frontend receives updates instantly, no polling required.
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{user_id}",
        {
            "type": "send_realtime_event",
            "data": data,
        },
    )


