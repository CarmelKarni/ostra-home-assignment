import unittest
from unittest.mock import Mock
from handlers import MessageHandler


class TestMessageHandlerDeleteMessage(unittest.TestCase):
    """Unit tests for MessageHandler.delete_message"""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_repo = Mock()
        self.mock_user_repo = Mock()
        self.handler = MessageHandler(self.mock_repo, self.mock_user_repo)

    def test_delete_message_success(self):
        """Test successful message deletion."""
        user_id = "user-123"
        message_id = 1

        self.mock_repo.delete.return_value = True

        result = self.handler.delete_message(user_id, message_id)

        self.assertTrue(result)
        self.mock_repo.delete.assert_called_once_with(message_id, user_id)

    def test_delete_message_not_found(self):
        """Test delete_message when message doesn't exist."""
        user_id = "user-123"
        message_id = 999

        self.mock_repo.delete.return_value = False

        result = self.handler.delete_message(user_id, message_id)

        self.assertFalse(result)

    def test_delete_message_missing_user_id(self):
        """Test delete_message with missing user_id."""
        with self.assertRaises(ValueError) as context:
            self.handler.delete_message(None, 1)

        self.assertEqual(str(context.exception), "user_id and message_id are required")

    def test_delete_message_missing_message_id(self):
        """Test delete_message with missing message_id."""
        with self.assertRaises(ValueError) as context:
            self.handler.delete_message("user-123", None)

        self.assertEqual(str(context.exception), "user_id and message_id are required")

    def test_delete_message_empty_user_id(self):
        """Test delete_message with empty user_id."""
        with self.assertRaises(ValueError) as context:
            self.handler.delete_message("", 1)

        self.assertEqual(str(context.exception), "user_id and message_id are required")

    def test_delete_message_zero_message_id(self):
        """Test delete_message with zero message_id."""
        with self.assertRaises(ValueError) as context:
            self.handler.delete_message("user-123", 0)

        self.assertEqual(str(context.exception), "user_id and message_id are required")

    def test_delete_message_repository_exception(self):
        """Test delete_message when repository raises exception."""
        self.mock_repo.delete.side_effect = Exception("Database error")

        with self.assertRaises(Exception) as context:
            self.handler.delete_message("user-123", 1)

        self.assertEqual(str(context.exception), "Database error")


class TestMessageHandlerDeleteMessages(unittest.TestCase):
    """Unit tests for MessageHandler.delete_messages"""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_repo = Mock()
        self.mock_user_repo = Mock()
        self.handler = MessageHandler(self.mock_repo, self.mock_user_repo)

    def test_delete_messages_success(self):
        """Test successful deletion of multiple messages."""
        user_id = "user-123"
        message_ids = [1, 2, 3]
        deleted_count = 3

        self.mock_repo.delete_batch.return_value = deleted_count

        result = self.handler.delete_messages(user_id, message_ids)

        self.assertEqual(result, deleted_count)
        self.mock_repo.delete_batch.assert_called_once_with(message_ids, user_id)

    def test_delete_messages_partial_success(self):
        """Test delete_messages when only some messages are deleted."""
        user_id = "user-123"
        message_ids = [1, 2, 3, 999]
        deleted_count = 3

        self.mock_repo.delete_batch.return_value = deleted_count

        result = self.handler.delete_messages(user_id, message_ids)

        self.assertEqual(result, 3)

    def test_delete_messages_empty_list(self):
        """Test delete_messages with empty message list."""
        user_id = "user-123"
        message_ids = []

        with self.assertRaises(ValueError) as context:
            self.handler.delete_messages(user_id, message_ids)

        self.assertEqual(str(context.exception), "user_id and message_ids are required")

    def test_delete_messages_missing_user_id(self):
        """Test delete_messages with missing user_id."""
        message_ids = [1, 2, 3]

        with self.assertRaises(ValueError) as context:
            self.handler.delete_messages(None, message_ids)

        self.assertEqual(str(context.exception), "user_id and message_ids are required")

    def test_delete_messages_missing_message_ids(self):
        """Test delete_messages with missing message_ids."""
        user_id = "user-123"

        with self.assertRaises(ValueError) as context:
            self.handler.delete_messages(user_id, None)

        self.assertEqual(str(context.exception), "user_id and message_ids are required")

    def test_delete_messages_empty_user_id(self):
        """Test delete_messages with empty user_id."""
        message_ids = [1, 2, 3]

        with self.assertRaises(ValueError) as context:
            self.handler.delete_messages("", message_ids)

        self.assertEqual(str(context.exception), "user_id and message_ids are required")

    def test_delete_messages_invalid_message_ids_type(self):
        """Test delete_messages with non-list message_ids."""
        user_id = "user-123"
        message_ids = "1,2,3"

        with self.assertRaises(ValueError) as context:
            self.handler.delete_messages(user_id, message_ids)

        self.assertEqual(str(context.exception), "message_ids must be a list")

    def test_delete_messages_single_message(self):
        """Test delete_messages with single message."""
        user_id = "user-123"
        message_ids = [1]
        deleted_count = 1

        self.mock_repo.delete_batch.return_value = deleted_count

        result = self.handler.delete_messages(user_id, message_ids)

        self.assertEqual(result, 1)

    def test_delete_messages_large_batch(self):
        """Test delete_messages with large batch of messages."""
        user_id = "user-123"
        message_ids = list(range(1, 101))
        deleted_count = 100

        self.mock_repo.delete_batch.return_value = deleted_count

        result = self.handler.delete_messages(user_id, message_ids)

        self.assertEqual(result, 100)

    def test_delete_messages_no_messages_deleted(self):
        """Test delete_messages when no messages are deleted."""
        user_id = "user-123"
        message_ids = [999, 1000, 1001]
        deleted_count = 0

        self.mock_repo.delete_batch.return_value = deleted_count

        result = self.handler.delete_messages(user_id, message_ids)

        self.assertEqual(result, 0)

    def test_delete_messages_repository_exception(self):
        """Test delete_messages when repository raises exception."""
        user_id = "user-123"
        message_ids = [1, 2, 3]
        self.mock_repo.delete_batch.side_effect = Exception("Database error")

        with self.assertRaises(Exception) as context:
            self.handler.delete_messages(user_id, message_ids)

        self.assertEqual(str(context.exception), "Database error")


if __name__ == '__main__':
    unittest.main()
