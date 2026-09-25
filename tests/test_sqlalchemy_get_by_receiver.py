import unittest
from unittest.mock import Mock, MagicMock, patch
from repositories.sqlalchemy_impl import SQLAlchemyMessageRepository


class TestSQLAlchemyMessageRepositoryGetByReceiver(unittest.TestCase):
    """Unit tests for SQLAlchemyMessageRepository.get_by_receiver"""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_db = Mock()
        self.mock_message_model = Mock()

        # Mock the message model's id attribute for filter operations
        self.mock_id = Mock()
        self.mock_id.__ge__ = Mock(return_value=Mock())
        self.mock_id.__lt__ = Mock(return_value=Mock())
        self.mock_id.in_ = Mock(return_value=Mock())

        self.mock_message_model.id = self.mock_id
        self.mock_message_model.receiver_id = Mock()
        self.mock_message_model.is_read = Mock()

        self.repo = SQLAlchemyMessageRepository(self.mock_db, self.mock_message_model)

    def test_get_by_receiver_success(self):
        """Test successful retrieval of messages by receiver."""
        receiver_id = "user-123"
        start_index = 0
        end_index = 10
        unread = False

        # Mock messages
        mock_messages = [
            Mock(id=i, receiver_id=receiver_id, to_dict=Mock(return_value={'id': i}))
            for i in range(1, 4)
        ]

        self.mock_message_model.query.filter.return_value.all.return_value = mock_messages

        result = self.repo.get_by_receiver(receiver_id, start_index, end_index, unread)

        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]['id'], 1)

    def test_get_by_receiver_empty_result(self):
        """Test get_by_receiver with no messages."""
        receiver_id = "user-123"
        start_index = 0
        end_index = 10
        unread = False

        self.mock_message_model.query.filter.return_value.all.return_value = []

        result = self.repo.get_by_receiver(receiver_id, start_index, end_index, unread)

        self.assertEqual(result, [])

    def test_get_by_receiver_with_range_filter(self):
        """Test get_by_receiver applies range filter correctly."""
        receiver_id = "user-123"
        start_index = 5
        end_index = 15
        unread = False

        mock_messages = [
            Mock(id=i, receiver_id=receiver_id, to_dict=Mock(return_value={'id': i}))
            for i in range(5, 15)
        ]

        self.mock_message_model.query.filter.return_value.all.return_value = mock_messages

        result = self.repo.get_by_receiver(receiver_id, start_index, end_index, unread)

        self.assertEqual(len(result), 10)
        # Verify filter was called
        self.mock_message_model.query.filter.assert_called_once()

    def test_get_by_receiver_negative_end_index(self):
        """Test get_by_receiver with negative end_index (no upper limit)."""
        receiver_id = "user-123"
        start_index = 0
        end_index = -1
        unread = False

        mock_messages = [
            Mock(id=i, receiver_id=receiver_id, to_dict=Mock(return_value={'id': i}))
            for i in range(1, 101)
        ]

        self.mock_message_model.query.filter.return_value.all.return_value = mock_messages

        result = self.repo.get_by_receiver(receiver_id, start_index, end_index, unread)

        self.assertEqual(len(result), 100)

    def test_get_by_receiver_large_range(self):
        """Test get_by_receiver with large range."""
        receiver_id = "user-123"
        start_index = 0
        end_index = 1000
        unread = False

        mock_messages = [
            Mock(id=i, receiver_id=receiver_id, to_dict=Mock(return_value={'id': i}))
            for i in range(1, 51)
        ]

        self.mock_message_model.query.filter.return_value.all.return_value = mock_messages

        result = self.repo.get_by_receiver(receiver_id, start_index, end_index, unread)

        self.assertEqual(len(result), 50)

    def test_get_by_receiver_with_unread_true(self):
        """Test get_by_receiver filters unread messages after query."""
        receiver_id = "user-123"
        start_index = 0
        end_index = 10
        unread = True

        # Create mocks with is_read attribute
        mock_msg1 = Mock(is_read=False, to_dict=Mock(return_value={'id': 1, 'isRead': False}))
        mock_msg2 = Mock(is_read=True, to_dict=Mock(return_value={'id': 2, 'isRead': True}))

        self.mock_message_model.query.filter.return_value.all.return_value = [mock_msg1, mock_msg2]

        result = self.repo.get_by_receiver(receiver_id, start_index, end_index, unread)

        # Only unread message should be returned
        self.assertEqual(len(result), 1)

    def test_get_by_receiver_with_unread_false(self):
        """Test get_by_receiver with unread=False parameter."""
        receiver_id = "user-123"
        start_index = 0
        end_index = 10
        unread = False

        mock_messages = [
            Mock(id=i, receiver_id=receiver_id, to_dict=Mock(return_value={'id': i}))
            for i in range(1, 4)
        ]

        self.mock_message_model.query.filter.return_value.all.return_value = mock_messages

        result = self.repo.get_by_receiver(receiver_id, start_index, end_index, unread)

        self.assertEqual(len(result), 3)

    def test_get_by_receiver_calls_to_dict(self):
        """Test that get_by_receiver calls to_dict on each message."""
        receiver_id = "user-123"
        start_index = 0
        end_index = 10
        unread = False

        mock_msg1 = Mock(id=1, receiver_id=receiver_id, to_dict=Mock(return_value={'id': 1}))
        mock_msg2 = Mock(id=2, receiver_id=receiver_id, to_dict=Mock(return_value={'id': 2}))

        self.mock_message_model.query.filter.return_value.all.return_value = [mock_msg1, mock_msg2]

        result = self.repo.get_by_receiver(receiver_id, start_index, end_index, unread)

        self.assertEqual(len(result), 2)
        mock_msg1.to_dict.assert_called_once()
        mock_msg2.to_dict.assert_called_once()

    def test_get_by_receiver_single_message(self):
        """Test get_by_receiver with single message."""
        receiver_id = "user-123"
        start_index = 0
        end_index = 10
        unread = False

        mock_messages = [
            Mock(id=1, receiver_id=receiver_id, to_dict=Mock(return_value={'id': 1}))
        ]

        self.mock_message_model.query.filter.return_value.all.return_value = mock_messages

        result = self.repo.get_by_receiver(receiver_id, start_index, end_index, unread)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['id'], 1)

    def test_get_by_receiver_respects_range(self):
        """Test get_by_receiver filters by message ID range."""
        receiver_id = "user-123"
        start_index = 10
        end_index = 20
        unread = False

        # Messages within range
        mock_messages = [
            Mock(id=i, receiver_id=receiver_id, to_dict=Mock(return_value={'id': i}))
            for i in range(10, 20)
        ]

        self.mock_message_model.query.filter.return_value.all.return_value = mock_messages

        result = self.repo.get_by_receiver(receiver_id, start_index, end_index, unread)

        self.assertEqual(len(result), 10)
        # Verify filter includes ID range check
        call_args = self.mock_message_model.query.filter.call_args
        self.assertIsNotNone(call_args)

    def test_get_by_receiver_filter_chain(self):
        """Test get_by_receiver builds correct filter chain."""
        receiver_id = "user-123"
        start_index = 0
        end_index = 10
        unread = False

        mock_query = Mock()
        mock_query.all.return_value = []
        self.mock_message_model.query.filter.return_value = mock_query

        self.repo.get_by_receiver(receiver_id, start_index, end_index, unread)

        # Verify query was called and filter applied
        self.mock_message_model.query.filter.assert_called_once()
        mock_query.all.assert_called_once()

    def test_get_by_receiver_multiple_messages_in_range(self):
        """Test get_by_receiver with multiple messages in specified range."""
        receiver_id = "user-123"
        start_index = 5
        end_index = 8
        unread = False

        mock_messages = [
            Mock(id=5, receiver_id=receiver_id, to_dict=Mock(return_value={'id': 5})),
            Mock(id=6, receiver_id=receiver_id, to_dict=Mock(return_value={'id': 6})),
            Mock(id=7, receiver_id=receiver_id, to_dict=Mock(return_value={'id': 7}))
        ]

        self.mock_message_model.query.filter.return_value.all.return_value = mock_messages

        result = self.repo.get_by_receiver(receiver_id, start_index, end_index, unread)

        self.assertEqual(len(result), 3)
        self.assertEqual([r['id'] for r in result], [5, 6, 7])


if __name__ == '__main__':
    unittest.main()
