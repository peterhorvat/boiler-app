from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken
from .consumers import NotificationConsumer, ChatConsumer
from unittest.mock import Mock, patch, AsyncMock
import asyncio
from tests.utils import generate_test_password

User = get_user_model()


class WebSocketConsumerTest(TestCase):
    def setUp(self):
        password1 = generate_test_password()
        password2 = generate_test_password()
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            username='user1',
            first_name='User',
            last_name='One',
            password=password1
        )
        self.user2 = User.objects.create_user(
            email='user2@example.com',
            username='user2',
            first_name='User',
            last_name='Two',
            password=password2
        )
        
        # Generate tokens
        self.token1 = AccessToken.for_user(self.user1)
        self.token2 = AccessToken.for_user(self.user2)


class NotificationConsumerTest(WebSocketConsumerTest):
    def setUp(self):
        super().setUp()
        self.consumer = NotificationConsumer()
        self.consumer.scope = {
            'url_route': {'kwargs': {'user_id': str(self.user1.id)}},
            'query_string': f'token={self.token1}'.encode()
        }

    @patch('apps.websockets.consumers.database_sync_to_async')
    def test_get_user_from_token_valid(self, mock_db_sync):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # Mock the database call to return user1
            async def mock_get_user(*args, **kwargs):
                return self.user1
            mock_db_sync.return_value = mock_get_user
            
            user = loop.run_until_complete(self.consumer.get_user_from_token())
            self.assertEqual(user, self.user1)
        finally:
            loop.close()

    def test_get_user_from_token_invalid(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # Use a simple invalid token string (not a real JWT)
            invalid_token = "invalid_token_string"
            self.consumer.scope['query_string'] = f'token={invalid_token}'.encode()
            user = loop.run_until_complete(self.consumer.get_user_from_token())
            self.assertIsNone(user)
        finally:
            loop.close()

    def test_get_user_from_token_no_token(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            self.consumer.scope['query_string'] = b''
            user = loop.run_until_complete(self.consumer.get_user_from_token())
            self.assertIsNone(user)
        finally:
            loop.close()

    def test_user_id_validation(self):
        # Test that user_id from URL is extracted correctly
        user_id = self.consumer.scope['url_route']['kwargs']['user_id']
        self.assertEqual(user_id, str(self.user1.id))

    @patch('apps.websockets.consumers.json.loads')
    def test_receive_ping_message(self, mock_json_loads):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        self.consumer.send = AsyncMock()
        mock_json_loads.return_value = {
            'type': 'ping',
            'timestamp': '2024-01-01T00:00:00Z'
        }
        
        try:
            loop.run_until_complete(self.consumer.receive('{"type":"ping","timestamp":"2024-01-01T00:00:00Z"}'))
            
            # Verify send was called with pong response
            self.consumer.send.assert_called_once()
            call_args = self.consumer.send.call_args[1]
            self.assertIn('type', call_args['text_data'])
            self.assertIn('pong', call_args['text_data'])
        finally:
            loop.close()

    def test_notification_message_structure(self):
        # Test the notification message structure
        event = {
            'message': 'Test notification',
            'notification_type': 'info',
            'timestamp': '2024-01-01T00:00:00Z'
        }
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        self.consumer.send = AsyncMock()
        
        try:
            loop.run_until_complete(self.consumer.notification_message(event))
            
            # Verify send was called
            self.consumer.send.assert_called_once()
            call_args = self.consumer.send.call_args[1]
            text_data = call_args['text_data']
            
            # Check that the message contains expected data
            self.assertIn('notification', text_data)
            self.assertIn('Test notification', text_data)
            self.assertIn('info', text_data)
        finally:
            loop.close()


class ChatConsumerTest(WebSocketConsumerTest):
    def setUp(self):
        super().setUp()
        self.consumer = ChatConsumer()
        self.consumer.scope = {
            'url_route': {'kwargs': {'room_name': 'testroom'}},
            'query_string': f'token={self.token1}'.encode()
        }
        self.consumer.user = self.user1

    def test_room_name_extraction(self):
        room_name = self.consumer.scope['url_route']['kwargs']['room_name']
        self.assertEqual(room_name, 'testroom')

    @patch('apps.websockets.consumers.database_sync_to_async')
    def test_get_user_from_token_valid(self, mock_db_sync):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # Mock the database call to return user1
            async def mock_get_user(*args, **kwargs):
                return self.user1
            mock_db_sync.return_value = mock_get_user
            
            user = loop.run_until_complete(self.consumer.get_user_from_token())
            self.assertEqual(user, self.user1)
        finally:
            loop.close()

    @patch('apps.websockets.consumers.json.loads')
    def test_receive_chat_message(self, mock_json_loads):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        self.consumer.channel_layer = Mock()
        self.consumer.channel_layer.group_send = AsyncMock()
        self.consumer.room_group_name = 'chat_testroom'
        
        mock_json_loads.return_value = {
            'message': 'Hello, world!',
            'type': 'chat_message'
        }
        
        try:
            loop.run_until_complete(
                self.consumer.receive('{"message":"Hello, world!","type":"chat_message"}')
            )
            
            # Verify group_send was called
            self.consumer.channel_layer.group_send.assert_called_once()
            call_args = self.consumer.channel_layer.group_send.call_args[0]
            
            # Check the group name and message content
            self.assertEqual(call_args[0], 'chat_testroom')
            message_data = call_args[1]
            self.assertEqual(message_data['message'], 'Hello, world!')
            self.assertEqual(message_data['user'], self.user1.username)
            self.assertEqual(message_data['user_id'], self.user1.id)
        finally:
            loop.close()

    def test_chat_message_event_handler(self):
        event = {
            'message': 'Hello, world!',
            'user': 'testuser',
            'user_id': 123,
            'message_type': 'chat_message',
            'timestamp': '2024-01-01T00:00:00Z'
        }
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        self.consumer.send = AsyncMock()
        
        try:
            loop.run_until_complete(self.consumer.chat_message(event))
            
            # Verify send was called
            self.consumer.send.assert_called_once()
            call_args = self.consumer.send.call_args[1]
            text_data = call_args['text_data']
            
            # Check that the message contains expected data
            self.assertIn('Hello, world!', text_data)
            self.assertIn('testuser', text_data)
            self.assertIn('chat_message', text_data)
        finally:
            loop.close()

    def test_user_joined_event_handler(self):
        event = {
            'user': 'testuser',
            'user_id': 123
        }
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        self.consumer.send = AsyncMock()
        
        try:
            loop.run_until_complete(self.consumer.user_joined(event))
            
            # Verify send was called with correct data
            self.consumer.send.assert_called_once()
            call_args = self.consumer.send.call_args[1]
            text_data = call_args['text_data']
            
            self.assertIn('user_joined', text_data)
            self.assertIn('testuser', text_data)
        finally:
            loop.close()

    def test_user_left_event_handler(self):
        event = {
            'user': 'testuser',
            'user_id': 123
        }
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        self.consumer.send = AsyncMock()
        
        try:
            loop.run_until_complete(self.consumer.user_left(event))
            
            # Verify send was called with correct data
            self.consumer.send.assert_called_once()
            call_args = self.consumer.send.call_args[1]
            text_data = call_args['text_data']
            
            self.assertIn('user_left', text_data)
            self.assertIn('testuser', text_data)
        finally:
            loop.close()

    def test_receive_invalid_json(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        self.consumer.send = AsyncMock()
        
        try:
            # Send actual invalid JSON (not mocked)
            loop.run_until_complete(self.consumer.receive('invalid json'))
            
            # Should send error message
            self.consumer.send.assert_called_once()
            call_args = self.consumer.send.call_args[1]
            text_data = call_args['text_data']
            
            self.assertIn('error', text_data)
            self.assertIn('Invalid message format', text_data)
        finally:
            loop.close()

    @patch('apps.websockets.consumers.json.loads')
    def test_receive_missing_message_key(self, mock_json_loads):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        self.consumer.send = AsyncMock()
        mock_json_loads.return_value = {'type': 'chat_message'}  # Missing 'message' key
        
        try:
            loop.run_until_complete(self.consumer.receive('{"type":"chat_message"}'))
            
            # Should send error message
            self.consumer.send.assert_called_once()
            call_args = self.consumer.send.call_args[1]
            text_data = call_args['text_data']
            
            self.assertIn('error', text_data)
            self.assertIn('Invalid message format', text_data)
        finally:
            loop.close()