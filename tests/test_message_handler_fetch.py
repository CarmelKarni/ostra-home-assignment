import unittest
from unittest.mock import Mock
from handlers import MessageHandler


class TestMessageHandlerFetchMessages(unittest.TestCase):
    """Unit tests for MessageHandler.fetch_messages"""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_repo = Mock()
        self.mock_user_repo = Mock()
        self.handler = MessageHandler(self.mock_repo, self.mock_user_repo)

    def test_fetch_messages_success(self):
        """Test successful message fetching."""
        receiver_id = "user-123"
        start_index = 0
        end_index = 10
        unread = False
        expected_messages = [
            {
                'id': 1,
                'senderId': 'user-456',
                'receiverId': receiver_id,
                'message': 'Hello 1',
                'timestamp': '2024-01-15T10:30:00Z',
                'isRead': False
            },
            {
                'id': 2,
                'senderId': 'user-789',
                'receiverId': receiver_id,
                'message': 'Hello 2',
                'timestamp': '2024-01-15T10:31:00Z',
                'isRead': True
            }
        ]

        self.mock_user_repo.get_by_id.return_value = {'id': receiver_id}
        self.mock_repo.get_by_receiver.return_value = expected_messages

        result = self.handler.fetch_messages(receiver_id, start_index, end_index, unread)

        self.assertEqual(result, expected_messages)
        self.mock_repo.get_by_receiver.assert_called_once_with(receiver_id, start_index, end_index, unread)

    def test_fetch_messages_empty_result(self):
        """Test fetch_messages with no messages."""
        receiver_id = "user-123"
        start_index = 0
        end_index = 10
        unread = False

        self.mock_user_repo.get_by_id.return_value = {'id': receiver_id}
        self.mock_repo.get_by_receiver.return_value = []

        result = self.handler.fetch_messages(receiver_id, start_index, end_index, unread)

        self.assertEqual(result, [])

    def test_fetch_messages_receiver_not_found(self):
        """Test fetch_messages with receiver not in users table."""
        self.mock_user_repo.get_by_id.return_value = None

        with self.assertRaises(ValueError) as context:
            self.handler.fetch_messages("unknown-receiver", 0, 10, False)

        self.assertEqual(str(context.exception), "Receiver not found")

    def test_fetch_messages_missing_receiver_id(self):
        """Test fetch_messages with missing receiver_id."""
        with self.assertRaises(ValueError) as context:
            self.handler.fetch_messages(None, 0, 10, False)

        self.assertEqual(str(context.exception), "receiver_id is required")

    def test_fetch_messages_empty_receiver_id(self):
        """Test fetch_messages with empty receiver_id."""
        with self.assertRaises(ValueError) as context:
            self.handler.fetch_messages("", 0, 10, False)

        self.assertEqual(str(context.exception), "receiver_id is required")

    def test_fetch_messages_negative_start_index(self):
        """Test fetch_messages with negative startIndex."""
        self.mock_user_repo.get_by_id.return_value = {'id': 'user-123'}

        with self.assertRaises(ValueError) as context:
            self.handler.fetch_messages("user-123", -1, 10, False)

        self.assertEqual(str(context.exception), "startIndex must be >= 0")

    def test_fetch_messages_end_index_less_than_start_index(self):
        """Test fetch_messages with endIndex <= startIndex."""
        self.mock_user_repo.get_by_id.return_value = {'id': 'user-123'}

        with self.assertRaises(ValueError) as context:
            self.handler.fetch_messages("user-123", 10, 5, False)

        self.assertEqual(str(context.exception), "endIndex must be > startIndex")

    def test_fetch_messages_end_index_equals_start_index(self):
        """Test fetch_messages with endIndex == startIndex."""
        self.mock_user_repo.get_by_id.return_value = {'id': 'user-123'}

        with self.assertRaises(ValueError) as context:
            self.handler.fetch_messages("user-123", 5, 5, False)

        self.assertEqual(str(context.exception), "endIndex must be > startIndex")

    def test_fetch_messages_with_custom_range(self):
        """Test fetch_messages with custom start and end indices."""
        receiver_id = "user-123"
        start_index = 5
        end_index = 15
        unread = False
        expected_messages = [
            {
                'id': i,
                'senderId': 'user-456',
                'receiverId': receiver_id,
                'message': f'Message {i}',
                'timestamp': '2024-01-15T10:30:00Z',
                'isRead': False
            }
            for i in range(start_index, end_index)
        ]

        self.mock_user_repo.get_by_id.return_value = {'id': receiver_id}
        self.mock_repo.get_by_receiver.return_value = expected_messages

        result = self.handler.fetch_messages(receiver_id, start_index, end_index, unread)

        self.assertEqual(result, expected_messages)
        self.mock_repo.get_by_receiver.assert_called_once_with(receiver_id, start_index, end_index, unread)

    def test_fetch_messages_repository_exception(self):
        """Test fetch_messages when repository raises exception."""
        self.mock_user_repo.get_by_id.return_value = {'id': 'user-123'}
        self.mock_repo.get_by_receiver.side_effect = Exception("Database error")

        with self.assertRaises(Exception) as context:
            self.handler.fetch_messages("user-123", 0, 10, False)

        self.assertEqual(str(context.exception), "Database error")

    def test_fetch_messages_large_range(self):
        """Test fetch_messages with large range."""
        receiver_id = "user-123"
        start_index = 0
        end_index = 1000
        unread = False
        expected_messages = []

        self.mock_user_repo.get_by_id.return_value = {'id': receiver_id}
        self.mock_repo.get_by_receiver.return_value = expected_messages

        result = self.handler.fetch_messages(receiver_id, start_index, end_index, unread)

        self.assertEqual(result, expected_messages)
        self.mock_repo.get_by_receiver.assert_called_once_with(receiver_id, start_index, end_index, unread)

    def test_fetch_messages_no_end_index(self):
        """Test fetch_messages with no end_index (end_index = -1) returns all messages."""
        receiver_id = "user-123"
        start_index = 0
        end_index = -1
        unread = False
        expected_messages = [
            {
                'id': 1,
                'senderId': 'user-456',
                'receiverId': receiver_id,
                'message': 'First message',
                'timestamp': '2024-01-15T10:00:00Z',
                'isRead': False
            },
            {
                'id': 2,
                'senderId': 'user-789',
                'receiverId': receiver_id,
                'message': 'Second message',
                'timestamp': '2024-01-15T10:30:00Z',
                'isRead': False
            },
            {
                'id': 3,
                'senderId': 'user-456',
                'receiverId': receiver_id,
                'message': 'Third message',
                'timestamp': '2024-01-15T11:00:00Z',
                'isRead': True
            }
        ]

        self.mock_user_repo.get_by_id.return_value = {'id': receiver_id}
        self.mock_repo.get_by_receiver.return_value = expected_messages

        result = self.handler.fetch_messages(receiver_id, start_index, end_index, unread)

        self.assertEqual(result, expected_messages)
        self.assertEqual(len(result), 3)
        self.mock_repo.get_by_receiver.assert_called_once_with(receiver_id, start_index, end_index, unread)

    def test_fetch_messages_returns_ascending_order(self):
        """Test fetch_messages returns messages in ascending order by timestamp."""
        receiver_id = "user-123"
        start_index = 0
        end_index = 10
        unread = False
        expected_messages = [
            {
                'id': 1,
                'senderId': 'user-456',
                'receiverId': receiver_id,
                'message': 'First message',
                'timestamp': '2024-01-15T10:00:00Z',
                'isRead': False
            },
            {
                'id': 2,
                'senderId': 'user-789',
                'receiverId': receiver_id,
                'message': 'Second message',
                'timestamp': '2024-01-15T10:30:00Z',
                'isRead': False
            },
            {
                'id': 3,
                'senderId': 'user-456',
                'receiverId': receiver_id,
                'message': 'Third message',
                'timestamp': '2024-01-15T11:00:00Z',
                'isRead': True
            }
        ]

        self.mock_user_repo.get_by_id.return_value = {'id': receiver_id}
        self.mock_repo.get_by_receiver.return_value = expected_messages

        result = self.handler.fetch_messages(receiver_id, start_index, end_index, unread)

        self.assertEqual(result, expected_messages)

        # Verify messages are in ascending order by timestamp
        for i in range(len(result) - 1):
            current_timestamp = result[i]['timestamp']
            next_timestamp = result[i + 1]['timestamp']
            self.assertLess(current_timestamp, next_timestamp,
                          f"Message {i} timestamp {current_timestamp} should be before {next_timestamp}")


class TestMessageHandlerFetchUnreadMessages(unittest.TestCase):
    """Unit tests for MessageHandler.fetch_unread_messages"""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_repo = Mock()
        self.mock_user_repo = Mock()
        self.handler = MessageHandler(self.mock_repo, self.mock_user_repo)

    def test_fetch_unread_messages_success(self):
        """Test successful unread messages fetching."""
        receiver_id = "user-123"
        expected_messages = [
            {
                'id': 1,
                'senderId': 'user-456',
                'receiverId': receiver_id,
                'message': 'Unread message 1',
                'timestamp': '2024-01-15T10:00:00Z',
                'isRead': False
            },
            {
                'id': 2,
                'senderId': 'user-789',
                'receiverId': receiver_id,
                'message': 'Unread message 2',
                'timestamp': '2024-01-15T10:30:00Z',
                'isRead': False
            }
        ]

        self.mock_user_repo.get_by_id.return_value = {'id': receiver_id}
        self.mock_repo.get_unread_by_receiver.return_value = expected_messages

        result = self.handler.fetch_unread_messages(receiver_id)

        self.assertEqual(result, expected_messages)
        self.assertEqual(len(result), 2)
        self.mock_repo.get_unread_by_receiver.assert_called_once_with(receiver_id)

    def test_fetch_unread_messages_empty_result(self):
        """Test fetch_unread_messages with no unread messages."""
        receiver_id = "user-123"

        self.mock_user_repo.get_by_id.return_value = {'id': receiver_id}
        self.mock_repo.get_unread_by_receiver.return_value = []

        result = self.handler.fetch_unread_messages(receiver_id)

        self.assertEqual(result, [])

    def test_fetch_unread_messages_receiver_not_found(self):
        """Test fetch_unread_messages with receiver not in users table."""
        self.mock_user_repo.get_by_id.return_value = None

        with self.assertRaises(ValueError) as context:
            self.handler.fetch_unread_messages("unknown-receiver")

        self.assertEqual(str(context.exception), "Receiver not found")

    def test_fetch_unread_messages_missing_receiver_id(self):
        """Test fetch_unread_messages with missing receiver_id."""
        with self.assertRaises(ValueError) as context:
            self.handler.fetch_unread_messages(None)

        self.assertEqual(str(context.exception), "receiver_id is required")

    def test_fetch_unread_messages_empty_receiver_id(self):
        """Test fetch_unread_messages with empty receiver_id."""
        with self.assertRaises(ValueError) as context:
            self.handler.fetch_unread_messages("")

        self.assertEqual(str(context.exception), "receiver_id is required")

    def test_fetch_unread_messages_all_marked_unread(self):
        """Test fetch_unread_messages returns only unread messages."""
        receiver_id = "user-123"
        expected_messages = [
            {
                'id': 1,
                'senderId': 'user-456',
                'receiverId': receiver_id,
                'message': 'Unread message',
                'timestamp': '2024-01-15T10:00:00Z',
                'isRead': False
            }
        ]

        self.mock_user_repo.get_by_id.return_value = {'id': receiver_id}
        self.mock_repo.get_unread_by_receiver.return_value = expected_messages

        result = self.handler.fetch_unread_messages(receiver_id)

        # Verify all returned messages have isRead=False
        for msg in result:
            self.assertFalse(msg['isRead'], f"Message {msg['id']} should be unread")

    def test_fetch_unread_messages_repository_exception(self):
        """Test fetch_unread_messages when repository raises exception."""
        self.mock_user_repo.get_by_id.return_value = {'id': 'user-123'}
        self.mock_repo.get_unread_by_receiver.side_effect = Exception("Database error")

        with self.assertRaises(Exception) as context:
            self.handler.fetch_unread_messages("user-123")

        self.assertEqual(str(context.exception), "Database error")

    def test_fetch_unread_messages_multiple_messages_mixed_status(self):
        """Test fetch_unread_messages returns only unread from mixed status."""
        receiver_id = "user-123"
        expected_messages = [
            {
                'id': 1,
                'senderId': 'user-456',
                'receiverId': receiver_id,
                'message': 'Unread message 1',
                'timestamp': '2024-01-15T10:00:00Z',
                'isRead': False
            },
            {
                'id': 3,
                'senderId': 'user-789',
                'receiverId': receiver_id,
                'message': 'Unread message 2',
                'timestamp': '2024-01-15T10:30:00Z',
                'isRead': False
            }
        ]

        self.mock_user_repo.get_by_id.return_value = {'id': receiver_id}
        self.mock_repo.get_unread_by_receiver.return_value = expected_messages

        result = self.handler.fetch_unread_messages(receiver_id)

        self.assertEqual(len(result), 2)
        # Verify no read messages are included (all should have isRead=False)
        for msg in result:
            self.assertFalse(msg['isRead'])


if __name__ == '__main__':
    unittest.main()

