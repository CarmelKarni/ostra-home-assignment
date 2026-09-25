from abc import ABC, abstractmethod
from typing import List, Optional


class UserRepository(ABC):
    """Abstract interface for user persistence."""

    @abstractmethod
    def create(self, name: str, email: str) -> dict:
        """Create a new user and return the user dict with id."""
        pass

    @abstractmethod
    def get_by_id(self, user_id: str) -> Optional[dict]:
        """Get a user by id. Return None if not found."""
        pass

    @abstractmethod
    def get_all(self) -> List[dict]:
        """Get all users."""
        pass

    @abstractmethod
    def update(self, user_id: str, name: Optional[str] = None, email: Optional[str] = None) -> Optional[dict]:
        """Update a user. Return updated user dict or None if not found."""
        pass

    @abstractmethod
    def delete(self, user_id: str) -> bool:
        """Delete a user. Return True if deleted, False if not found."""
        pass


class MessageRepository(ABC):
    """Abstract interface for message persistence."""

    @abstractmethod
    def create(self, sender_id: str, receiver_id: str, message: str) -> dict:
        """Create a new message and return the message dict with id."""
        pass

    @abstractmethod
    def get_by_id(self, message_id: int) -> Optional[dict]:
        """Get a message by id. Return None if not found."""
        pass

    @abstractmethod
    def get_by_receiver(self, receiver_id: str, start_index: int, end_index: int, unread: bool) -> List[dict]:
        """Get messages received by a user with pagination."""
        pass

    @abstractmethod
    def get_unread_by_receiver(self, receiver_id: str) -> List[dict]:
        """Get all unread messages for a receiver."""
        pass

    @abstractmethod
    def delete(self, message_id: int, user_id: str) -> bool:
        """Delete a message. Return True if deleted, False if not found or user doesn't own it."""
        pass

    @abstractmethod
    def delete_batch(self, message_ids: List[int], user_id: str) -> int:
        """Delete multiple messages. Return count of deleted messages."""
        pass

    @abstractmethod
    def update_read_status(self, message_id: int, is_read: bool, user_id: str) -> Optional[dict]:
        """Update message read status. Return updated message dict or None if not found or user is not receiver."""
        pass

