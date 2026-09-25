import unittest
from unittest.mock import Mock, patch, MagicMock
from handlers import MessageHandler


class TestMessageHandlerSendMessage(unittest.TestCase):
    """Unit tests for MessageHandler.send_message"""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_repo = Mock()
        self.mock_user_repo = Mock()
        self.handler = MessageHandler(self.mock_repo, self.mock_user_repo)

    def test_send_message_success(self):
        """Test successful message sending."""
        sender_id = "user-123"
        receiver_id = "user-456"
        message = "Hello, world!"
        expected_result = {
            'id': 1,
            'senderId': sender_id,
            'receiverId': receiver_id,
            'message': message,
            'timestamp': '2024-01-15T10:30:00Z',
            'isRead': False
        }

        self.mock_user_repo.get_by_id.side_effect = lambda uid: {'id': uid}
        self.mock_repo.create.return_value = expected_result

        result = self.handler.send_message(sender_id, receiver_id, message)

        self.assertEqual(result, expected_result)
        self.mock_repo.create.assert_called_once_with(sender_id, receiver_id, message)

    def test_send_message_missing_sender_id(self):
        """Test send_message with missing sender_id."""
        with self.assertRaises(ValueError) as context:
            self.handler.send_message(None, "user-456", "Hello")

        self.assertEqual(str(context.exception), "sender_id, receiver_id, and message are required")

    def test_send_message_missing_receiver_id(self):
        """Test send_message with missing receiver_id."""
        with self.assertRaises(ValueError) as context:
            self.handler.send_message("user-123", None, "Hello")

        self.assertEqual(str(context.exception), "sender_id, receiver_id, and message are required")

    def test_send_message_missing_message(self):
        """Test send_message with missing message."""
        with self.assertRaises(ValueError) as context:
            self.handler.send_message("user-123", "user-456", None)

        self.assertEqual(str(context.exception), "sender_id, receiver_id, and message are required")

    def test_send_message_empty_string_values(self):
        """Test send_message with empty string values."""
        with self.assertRaises(ValueError) as context:
            self.handler.send_message("", "user-456", "Hello")

        self.assertEqual(str(context.exception), "sender_id, receiver_id, and message are required")

    def test_send_message_message_too_long(self):
        """Test send_message with message exceeding 1000 characters."""
        sender_id = "user-123"
        receiver_id = "user-456"
        message = "x" * 1001

        with self.assertRaises(ValueError) as context:
            self.handler.send_message(sender_id, receiver_id, message)

        self.assertEqual(str(context.exception), "message exceeds 1000 character limit")

    def test_send_message_sender_not_found(self):
        """Test send_message with sender not in users table."""
        self.mock_user_repo.get_by_id.return_value = None

        with self.assertRaises(ValueError) as context:
            self.handler.send_message("unknown-sender", "user-456", "Hello")

        self.assertEqual(str(context.exception), "Sender not found")

    def test_send_message_receiver_not_found(self):
        """Test send_message with receiver not in users table."""
        self.mock_user_repo.get_by_id.side_effect = lambda uid: {'id': uid} if uid == "user-123" else None

        with self.assertRaises(ValueError) as context:
            self.handler.send_message("user-123", "unknown-receiver", "Hello")

        self.assertEqual(str(context.exception), "Receiver not found")

    def test_send_message_exactly_1000_characters(self):
        """Test send_message with message exactly 1000 characters."""
        sender_id = "user-123"
        receiver_id = "user-456"
        message = "x" * 1000
        expected_result = {
            'id': 1,
            'senderId': sender_id,
            'receiverId': receiver_id,
            'message': message,
            'timestamp': '2024-01-15T10:30:00Z',
            'isRead': False
        }

        self.mock_user_repo.get_by_id.side_effect = lambda uid: {'id': uid}
        self.mock_repo.create.return_value = expected_result

        result = self.handler.send_message(sender_id, receiver_id, message)

        self.assertEqual(result, expected_result)
        self.mock_repo.create.assert_called_once_with(sender_id, receiver_id, message)

    def test_send_message_repository_exception(self):
        """Test send_message when repository raises exception."""
        self.mock_repo.create.side_effect = Exception("Database error")

        with self.assertRaises(Exception) as context:
            self.handler.send_message("user-123", "user-456", "Hello")

        self.assertEqual(str(context.exception), "Database error")

    def test_send_message_special_characters(self):
        """Test send_message with special characters."""
        sender_id = "user-123"
        receiver_id = "user-456"
        message = "Hello! @#$%^&*() 你好 🎉"
        expected_result = {
            'id': 1,
            'senderId': sender_id,
            'receiverId': receiver_id,
            'message': message,
            'timestamp': '2024-01-15T10:30:00Z',
            'isRead': False
        }

        self.mock_user_repo.get_by_id.side_effect = lambda uid: {'id': uid}
        self.mock_repo.create.return_value = expected_result

        result = self.handler.send_message(sender_id, receiver_id, message)

        self.assertEqual(result, expected_result)
        self.mock_repo.create.assert_called_once_with(sender_id, receiver_id, message)

    def test_send_message_whitespace_only_message(self):
        """Test send_message with whitespace-only message."""
        # Whitespace-only message is not empty, so it should pass initial validation
        sender_id = "user-123"
        receiver_id = "user-456"
        message = "   "
        expected_result = {
            'id': 1,
            'senderId': sender_id,
            'receiverId': receiver_id,
            'message': message,
            'timestamp': '2024-01-15T10:30:00Z',
            'isRead': False
        }

        self.mock_user_repo.get_by_id.side_effect = lambda uid: {'id': uid}
        self.mock_repo.create.return_value = expected_result

        result = self.handler.send_message(sender_id, receiver_id, message)

        self.assertEqual(result, expected_result)


if __name__ == '__main__':
    unittest.main()
