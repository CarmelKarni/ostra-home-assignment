import unittest
from unittest.mock import Mock, MagicMock, patch
from repositories.sqlalchemy_impl import SQLAlchemyMessageRepository


class TestSQLAlchemyMessageRepositoryUpdateReadStatus(unittest.TestCase):
    """Unit tests for SQLAlchemyMessageRepository.update_read_status"""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_db = Mock()
        self.mock_message_model = Mock()
        self.repo = SQLAlchemyMessageRepository(self.mock_db, self.mock_message_model)

    def test_update_read_status_success_mark_as_read(self):
        """Test successful update of read status to True."""
        message_id = 1
        user_id = "user-123"
        is_read = True

        mock_message = Mock(id=message_id, receiver_id=user_id, is_read=False)
        mock_message.to_dict = Mock(return_value={'id': message_id, 'isRead': True})
        self.mock_message_model.query.get.return_value = mock_message

        result = self.repo.update_read_status(message_id, is_read, user_id)

        self.assertEqual(result['id'], message_id)
        self.assertTrue(result['isRead'])
        self.assertEqual(mock_message.is_read, True)
        self.mock_db.session.commit.assert_called_once()

    def test_update_read_status_success_mark_as_unread(self):
        """Test successful update of read status to False."""
        message_id = 1
        user_id = "user-123"
        is_read = False

        mock_message = Mock(id=message_id, receiver_id=user_id, is_read=True)
        mock_message.to_dict = Mock(return_value={'id': message_id, 'isRead': False})
        self.mock_message_model.query.get.return_value = mock_message

        result = self.repo.update_read_status(message_id, is_read, user_id)

        self.assertEqual(result['id'], message_id)
        self.assertFalse(result['isRead'])
        self.assertEqual(mock_message.is_read, False)
        self.mock_db.session.commit.assert_called_once()

    def test_update_read_status_message_not_found(self):
        """Test update_read_status when message doesn't exist."""
        message_id = 999
        user_id = "user-123"
        is_read = True

        self.mock_message_model.query.get.return_value = None

        result = self.repo.update_read_status(message_id, is_read, user_id)

        self.assertIsNone(result)
        self.mock_db.session.commit.assert_not_called()

    def test_update_read_status_user_not_receiver(self):
        """Test update_read_status when user is not the receiver."""
        message_id = 1
        user_id = "user-123"
        is_read = True

        mock_message = Mock(id=message_id, receiver_id="user-456")
        self.mock_message_model.query.get.return_value = mock_message

        result = self.repo.update_read_status(message_id, is_read, user_id)

        self.assertIsNone(result)
        self.mock_db.session.commit.assert_not_called()

    def test_update_read_status_authorization_check(self):
        """Test that update_read_status checks receiver ownership."""
        message_id = 1
        user_id = "user-123"
        different_user_id = "user-999"
        is_read = True

        mock_message = Mock(id=message_id, receiver_id=different_user_id)
        self.mock_message_model.query.get.return_value = mock_message

        result = self.repo.update_read_status(message_id, is_read, user_id)

        self.assertIsNone(result)

    def test_update_read_status_database_error(self):
        """Test update_read_status when database error occurs."""
        message_id = 1
        user_id = "user-123"
        is_read = True

        mock_message = Mock(id=message_id, receiver_id=user_id)
        self.mock_message_model.query.get.return_value = mock_message
        self.mock_db.session.commit.side_effect = Exception("Database error")

        with self.assertRaises(Exception) as context:
            self.repo.update_read_status(message_id, is_read, user_id)

        self.assertEqual(str(context.exception), "Database error")
        self.mock_db.session.rollback.assert_called_once()

    def test_update_read_status_rollback_on_error(self):
        """Test that rollback is called on error."""
        message_id = 1
        user_id = "user-123"
        is_read = True

        mock_message = Mock(id=message_id, receiver_id=user_id)
        self.mock_message_model.query.get.return_value = mock_message
        self.mock_db.session.commit.side_effect = Exception("Commit failed")

        try:
            self.repo.update_read_status(message_id, is_read, user_id)
        except Exception:
            pass

        self.mock_db.session.rollback.assert_called_once()

    def test_update_read_status_calls_to_dict(self):
        """Test that update_read_status calls to_dict on message."""
        message_id = 1
        user_id = "user-123"
        is_read = True

        mock_message = Mock(id=message_id, receiver_id=user_id)
        mock_message.to_dict = Mock(return_value={'id': message_id, 'isRead': True})
        self.mock_message_model.query.get.return_value = mock_message

        result = self.repo.update_read_status(message_id, is_read, user_id)

        mock_message.to_dict.assert_called_once()
        self.assertEqual(result['id'], message_id)

    def test_update_read_status_multiple_updates(self):
        """Test updating read status multiple times."""
        message_id = 1
        user_id = "user-123"

        mock_message = Mock(id=message_id, receiver_id=user_id, is_read=False)
        mock_message.to_dict = Mock(side_effect=[
            {'id': message_id, 'isRead': True},
            {'id': message_id, 'isRead': False}
        ])
        self.mock_message_model.query.get.return_value = mock_message

        # First update: mark as read
        result1 = self.repo.update_read_status(message_id, True, user_id)
        self.assertTrue(result1['isRead'])

        # Second update: mark as unread
        result2 = self.repo.update_read_status(message_id, False, user_id)
        self.assertFalse(result2['isRead'])

        self.assertEqual(self.mock_db.session.commit.call_count, 2)

    def test_update_read_status_same_status(self):
        """Test updating to the same read status."""
        message_id = 1
        user_id = "user-123"
        is_read = True

        mock_message = Mock(id=message_id, receiver_id=user_id, is_read=True)
        mock_message.to_dict = Mock(return_value={'id': message_id, 'isRead': True})
        self.mock_message_model.query.get.return_value = mock_message

        result = self.repo.update_read_status(message_id, is_read, user_id)

        self.assertEqual(result['id'], message_id)
        self.assertTrue(result['isRead'])
        self.mock_db.session.commit.assert_called_once()

    def test_update_read_status_returns_updated_message_dict(self):
        """Test that update_read_status returns complete message dict."""
        message_id = 1
        user_id = "user-123"
        is_read = True

        mock_message = Mock(id=message_id, receiver_id=user_id)
        expected_dict = {
            'id': message_id,
            'senderId': 'user-456',
            'receiverId': user_id,
            'message': 'test message',
            'isRead': True,
            'timestamp': '2026-09-24T10:00:00'
        }
        mock_message.to_dict = Mock(return_value=expected_dict)
        self.mock_message_model.query.get.return_value = mock_message

        result = self.repo.update_read_status(message_id, is_read, user_id)

        self.assertEqual(result, expected_dict)


if __name__ == '__main__':
    unittest.main()
