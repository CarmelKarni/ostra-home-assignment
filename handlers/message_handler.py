from typing import Optional, List


class MessageHandler:
    """Business logic layer for message operations."""

    def __init__(self, message_repo, user_repo):
        self.message_repo = message_repo
        self.user_repo = user_repo

    def send_message(self, sender_id: str, receiver_id: str, message: str) -> dict:
        """Send a message with validation."""
        if not sender_id or not receiver_id or not message:
            raise ValueError("sender_id, receiver_id, and message are required")

        if len(message) > 1000:
            raise ValueError("message exceeds 1000 character limit")

        sender = self.user_repo.get_by_id(sender_id)
        if not sender:
            raise ValueError("Sender not found")

        receiver = self.user_repo.get_by_id(receiver_id)
        if not receiver:
            raise ValueError("Receiver not found")

        return self.message_repo.create(sender_id, receiver_id, message)

    def fetch_messages(self, receiver_id: str, start_index: int, end_index: int, unread: bool) -> List[dict]:
        """Fetch messages for a user with pagination."""
        if not receiver_id:
            raise ValueError("receiver_id is required")

        receiver = self.user_repo.get_by_id(receiver_id)
        if not receiver:
            raise ValueError("Receiver not found")

        if start_index < 0:
            raise ValueError("startIndex must be >= 0")

        if start_index >= end_index >= 0:
            raise ValueError("endIndex must be > startIndex")

        return self.message_repo.get_by_receiver(receiver_id, start_index, end_index, unread)

    def fetch_unread_messages(self, receiver_id: str) -> List[dict]:
        """Fetch all unread messages for a user."""
        if not receiver_id:
            raise ValueError("receiver_id is required")

        receiver = self.user_repo.get_by_id(receiver_id)
        if not receiver:
            raise ValueError("Receiver not found")

        return self.message_repo.get_unread_by_receiver(receiver_id)

    def delete_message(self, user_id: str, message_id: int) -> bool:
        """Delete a single message."""
        if not user_id or not message_id:
            raise ValueError("user_id and message_id are required")

        return self.message_repo.delete(message_id, user_id)

    def delete_messages(self, user_id: str, message_ids: List[int]) -> int:
        """Delete multiple messages."""
        if not user_id or not message_ids:
            raise ValueError("user_id and message_ids are required")

        if not isinstance(message_ids, list):
            raise ValueError("message_ids must be a list")

        return self.message_repo.delete_batch(message_ids, user_id)

    def change_read_status(self, user_id: str, message_id: int, is_read: bool) -> dict:
        """Change the read status of a message."""
        if not user_id or not message_id:
            raise ValueError("user_id and message_id are required")

        if is_read is None:
            raise ValueError("is_read status is required")

        return self.message_repo.update_read_status(message_id, is_read, user_id)
