import json
from channels.generic.websocket import AsyncWebsocketConsumer

class SharedTextConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Add client to the "shared_text" group
        self.room_group_name = 'shared_text'
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Remove client from the "shared_text" group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Receive message from WebSocket
        text_data_json = json.loads(text_data)
        shared_text = text_data_json['shared_text']

        # Send message to all clients in the "shared_text" group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'shared_text_message',
                'shared_text': shared_text
            }
        )

    async def shared_text_message(self, event):
        # Send message to WebSocket
        shared_text = event['shared_text']
        await self.send(text_data=json.dumps({
            'shared_text': shared_text
        }))
