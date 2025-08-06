import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from jwt.exceptions import DecodeError

User = get_user_model()


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.room_group_name = f'notifications_{self.user_id}'
        
        # Authenticate user
        user = await self.get_user_from_token()
        if not user or str(user.id) != self.user_id:
            await self.close()
            return
        
        self.user = user
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': f'Connected to notifications for user {self.user_id}'
        }))

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type')
            
            if message_type == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': text_data_json.get('timestamp')
                }))
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))

    # Receive message from room group
    async def notification_message(self, event):
        message = event['message']
        notification_type = event.get('notification_type', 'info')
        
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'notification_type': notification_type,
            'message': message,
            'timestamp': event.get('timestamp')
        }))

    async def get_user_from_token(self):
        """Extract user from JWT token in query string"""
        try:
            # Get token from query string
            query_string = self.scope.get('query_string', b'').decode()
            token = None
            
            for param in query_string.split('&'):
                if param.startswith('token='):
                    token = param.split('=', 1)[1]
                    break
            
            if not token:
                return None
            
            # Validate token
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            
            # Get user from database
            user = await database_sync_to_async(User.objects.get)(id=user_id)
            return user
            
        except (InvalidToken, TokenError, DecodeError, User.DoesNotExist, Exception):
            return None


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        
        # Authenticate user
        user = await self.get_user_from_token()
        if not user:
            await self.close()
            return
        
        self.user = user
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Notify room that user joined
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_joined',
                'user': self.user.username,
                'user_id': self.user.id
            }
        )

    async def disconnect(self, close_code):
        # Notify room that user left
        if hasattr(self, 'user'):
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_left',
                    'user': self.user.username,
                    'user_id': self.user.id
                }
            )
        
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json['message']
            message_type = text_data_json.get('type', 'chat_message')
            
            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'user': self.user.username,
                    'user_id': self.user.id,
                    'message_type': message_type
                }
            )
        except (json.JSONDecodeError, KeyError):
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid message format'
            }))

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        user = event['user']
        user_id = event['user_id']
        message_type = event.get('message_type', 'chat_message')
        
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': message_type,
            'message': message,
            'user': user,
            'user_id': user_id,
            'timestamp': event.get('timestamp')
        }))

    async def user_joined(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_joined',
            'user': event['user'],
            'user_id': event['user_id']
        }))

    async def user_left(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_left',
            'user': event['user'],
            'user_id': event['user_id']
        }))

    async def get_user_from_token(self):
        """Extract user from JWT token in query string"""
        try:
            # Get token from query string
            query_string = self.scope.get('query_string', b'').decode()
            token = None
            
            for param in query_string.split('&'):
                if param.startswith('token='):
                    token = param.split('=', 1)[1]
                    break
            
            if not token:
                return None
            
            # Validate token
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            
            # Get user from database
            user = await database_sync_to_async(User.objects.get)(id=user_id)
            return user
            
        except (InvalidToken, TokenError, DecodeError, User.DoesNotExist, Exception):
            return None