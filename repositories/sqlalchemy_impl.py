from typing import List, Optional
from .base import UserRepository, MessageRepository


class SQLAlchemyUserRepository(UserRepository):
    """SQLAlchemy implementation of UserRepository."""

    def __init__(self, db, User):
        self.db = db
        self.User = User

    def create(self, name: str, email: str) -> dict:
        try:
            user = self.User(name=name, email=email)
            self.db.session.add(user)
            self.db.session.commit()
            return user.to_dict()
        except Exception as e:
            self.db.session.rollback()
            raise

    def get_by_id(self, user_id: str) -> Optional[dict]:
        user = self.User.query.get(user_id)
        return user.to_dict() if user else None

    def get_all(self) -> List[dict]:
        users = self.User.query.all()
        return [user.to_dict() for user in users]

    def update(self, user_id: str, name: Optional[str] = None, email: Optional[str] = None) -> Optional[dict]:
        user = self.User.query.get(user_id)
        if not user:
            return None

        try:
            if name is not None:
                user.name = name
            if email is not None:
                user.email = email

            self.db.session.commit()
            return user.to_dict()
        except Exception as e:
            self.db.session.rollback()
            raise

    def delete(self, user_id: str) -> bool:
        user = self.User.query.get(user_id)
        if not user:
            return False

        try:
            self.db.session.delete(user)
            self.db.session.commit()
            return True
        except Exception as e:
            self.db.session.rollback()
            raise


class SQLAlchemyMessageRepository(MessageRepository):
    """SQLAlchemy implementation of MessageRepository."""

    def __init__(self, db, Message):
        self.db = db
        self.Message = Message

    def create(self, sender_id: str, receiver_id: str, message: str) -> dict:
        try:
            msg = self.Message(sender_id=sender_id, receiver_id=receiver_id, message=message)
            self.db.session.add(msg)
            self.db.session.commit()
            return msg.to_dict()
        except Exception as e:
            self.db.session.rollback()
            raise

    def get_by_id(self, message_id: int) -> Optional[dict]:
        msg = self.Message.query.get(message_id)
        return msg.to_dict() if msg else None

    def get_by_receiver(self, receiver_id: str, start_index: int, end_index: int, unread: bool) -> List[dict]:
        if end_index < 0:
            end_index = float('inf')  # No upper limit if end_index is negative
        messages = self.Message.query.filter(
            self.Message.receiver_id == receiver_id,
            self.Message.id >= start_index,
            self.Message.id < end_index
        ).all()
        if unread:
            messages = [msg for msg in messages if not msg.is_read]
        return [msg.to_dict() for msg in messages]

    def get_unread_by_receiver(self, receiver_id: str) -> List[dict]:
        messages = self.Message.query.filter_by(receiver_id=receiver_id, is_read=False).all()
        return [msg.to_dict() for msg in messages]

    def delete(self, message_id: int, user_id: str) -> bool:
        msg = self.Message.query.get(message_id)
        if not msg or msg.receiver_id != user_id:
            return False

        try:
            self.db.session.delete(msg)
            self.db.session.commit()
            return True
        except Exception as e:
            self.db.session.rollback()
            raise

    def delete_batch(self, message_ids: List[int], user_id: str) -> int:
        try:
            messages = self.Message.query.filter(self.Message.id.in_(message_ids)).all()
            deleted_count = 0
            for msg in messages:
                if msg.receiver_id == user_id:
                    self.db.session.delete(msg)
                    deleted_count += 1

            self.db.session.commit()
            return deleted_count
        except Exception as e:
            self.db.session.rollback()
            raise

    def update_read_status(self, message_id: int, is_read: bool, user_id: str) -> Optional[dict]:
        msg = self.Message.query.get(message_id)
        if not msg or msg.receiver_id != user_id:
            return None

        try:
            msg.is_read = is_read
            self.db.session.commit()
            return msg.to_dict()
        except Exception as e:
            self.db.session.rollback()
            raise

