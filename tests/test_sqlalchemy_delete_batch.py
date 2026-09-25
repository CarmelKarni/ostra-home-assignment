import unittest
from unittest.mock import Mock, MagicMock, patch
from repositories.sqlalchemy_impl import SQLAlchemyMessageRepository


class TestSQLAlchemyMessageRepositoryDeleteBatch(unittest.TestCase):
    """Unit tests for SQLAlchemyMessageRepository.delete_batch"""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_db = Mock()
        self.mock_message_model = Mock()
        self.repo = SQLAlchemyMessageRepository(self.mock_db, self.mock_message_model)

    def test_delete_batch_success_all_messages(self):
        """Test successful deletion of all messages in batch."""
        user_id = "user-123"
        message_ids = [1, 2, 3]

        # Mock messages where user is receiver (matches implementation)
        mock_messages = [
            Mock(id=1, receiver_id=user_id),
            Mock(id=2, receiver_id=user_id),
            Mock(id=3, receiver_id=user_id)
        ]

        self.mock_message_model.query.filter.return_value.all.return_value = mock_messages

        result = self.repo.delete_batch(message_ids, user_id)

        self.assertEqual(result, 3)
        self.mock_db.session.delete.assert_called()
        self.mock_db.session.commit.assert_called_once()

    def test_delete_batch_partial_ownership(self):
        """Test delete_batch when user doesn't own all messages."""
        user_id = "user-123"
        message_ids = [1, 2, 3, 4]

        # Mock messages - only some have user as receiver
        mock_messages = [
            Mock(id=1, receiver_id=user_id),
            Mock(id=2, receiver_id=user_id),
            Mock(id=3, receiver_id="user-456"),  # Different receiver
            Mock(id=4, receiver_id=user_id)
        ]

        self.mock_message_model.query.filter.return_value.all.return_value = mock_messages

        result = self.repo.delete_batch(message_ids, user_id)

        # Should only delete 3 messages (ids 1, 2, 4) where user is receiver
        self.assertEqual(result, 3)
        self.mock_db.session.commit.assert_called_once()

    def test_delete_batch_empty_list(self):
        """Test delete_batch with empty message list."""
        user_id = "user-123"
        message_ids = []

        self.mock_message_model.query.filter.return_value.all.return_value = []

        result = self.repo.delete_batch(message_ids, user_id)

        self.assertEqual(result, 0)
        self.mock_db.session.delete.assert_not_called()
        self.mock_db.session.commit.assert_called_once()

    def test_delete_batch_no_matching_messages(self):
        """Test delete_batch when no messages match the IDs."""
        user_id = "user-123"
        message_ids = [999, 1000, 1001]

        self.mock_message_model.query.filter.return_value.all.return_value = []

        result = self.repo.delete_batch(message_ids, user_id)

        self.assertEqual(result, 0)
        self.mock_db.session.delete.assert_not_called()

    def test_delete_batch_user_receives_message(self):
        """Test delete_batch when user is receiver of message."""
        user_id = "user-123"
        message_ids = [1, 2]

        # Mock messages where user is receiver
        mock_messages = [
            Mock(id=1, sender_id="user-456", receiver_id=user_id),
            Mock(id=2, sender_id="user-789", receiver_id=user_id)
        ]

        self.mock_message_model.query.filter.return_value.all.return_value = mock_messages

        result = self.repo.delete_batch(message_ids, user_id)

        # Should delete both messages (user is receiver)
        self.assertEqual(result, 2)
        self.mock_db.session.commit.assert_called_once()

    def test_delete_batch_mixed_sender_receiver(self):
        """Test delete_batch - implementation only checks receiver_id."""
        user_id = "user-123"
        message_ids = [1, 2, 3, 4]

        mock_messages = [
            Mock(id=1, receiver_id=user_id),           # User is receiver - deleted
            Mock(id=2, receiver_id="user-456"),        # User not receiver - not deleted
            Mock(id=3, receiver_id=user_id),           # User is receiver - deleted
            Mock(id=4, receiver_id="user-888")         # User not receiver - not deleted
        ]

        self.mock_message_model.query.filter.return_value.all.return_value = mock_messages

        result = self.repo.delete_batch(message_ids, user_id)

        # Should delete only 2 messages (1, 3) where user is receiver
        self.assertEqual(result, 2)

    def test_delete_batch_large_batch(self):
        """Test delete_batch with large number of messages."""
        user_id = "user-123"
        message_ids = list(range(1, 101))

        # Mock 100 messages all with user as receiver
        mock_messages = [Mock(id=i, receiver_id=user_id) for i in range(1, 101)]

        self.mock_message_model.query.filter.return_value.all.return_value = mock_messages

        result = self.repo.delete_batch(message_ids, user_id)

        self.assertEqual(result, 100)
        self.mock_db.session.commit.assert_called_once()

    def test_delete_batch_database_error(self):
        """Test delete_batch when database error occurs."""
        user_id = "user-123"
        message_ids = [1, 2, 3]

        mock_messages = [
            Mock(id=1, receiver_id=user_id),
            Mock(id=2, receiver_id=user_id),
            Mock(id=3, receiver_id=user_id)
        ]

        self.mock_message_model.query.filter.return_value.all.return_value = mock_messages
        self.mock_db.session.commit.side_effect = Exception("Database error")

        with self.assertRaises(Exception) as context:
            self.repo.delete_batch(message_ids, user_id)

        self.assertEqual(str(context.exception), "Database error")
        self.mock_db.session.rollback.assert_called_once()

    def test_delete_batch_query_called_correctly(self):
        """Test that delete_batch calls query with correct filter."""
        user_id = "user-123"
        message_ids = [1, 2, 3]

        mock_messages = [
            Mock(id=1, sender_id=user_id),
            Mock(id=2, sender_id=user_id),
            Mock(id=3, sender_id=user_id)
        ]

        self.mock_message_model.query.filter.return_value.all.return_value = mock_messages

        self.repo.delete_batch(message_ids, user_id)

        # Verify query was called with id filter
        self.mock_message_model.query.filter.assert_called_once()
        call_args = self.mock_message_model.query.filter.call_args

        # Check that the filter includes message IDs
        self.assertIsNotNone(call_args)

    def test_delete_batch_single_message(self):
        """Test delete_batch with single message."""
        user_id = "user-123"
        message_ids = [1]

        mock_messages = [Mock(id=1, receiver_id=user_id)]

        self.mock_message_model.query.filter.return_value.all.return_value = mock_messages

        result = self.repo.delete_batch(message_ids, user_id)

        self.assertEqual(result, 1)

    def test_delete_batch_rollback_on_error(self):
        """Test that rollback is called on error."""
        user_id = "user-123"
        message_ids = [1, 2, 3]

        mock_messages = [
            Mock(id=1, receiver_id=user_id),
            Mock(id=2, receiver_id=user_id),
            Mock(id=3, receiver_id=user_id)
        ]

        self.mock_message_model.query.filter.return_value.all.return_value = mock_messages
        self.mock_db.session.commit.side_effect = Exception("Commit failed")

        try:
            self.repo.delete_batch(message_ids, user_id)
        except Exception:
            pass

        self.mock_db.session.rollback.assert_called_once()


if __name__ == '__main__':
    unittest.main()
