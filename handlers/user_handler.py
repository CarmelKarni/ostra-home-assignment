from typing import Optional


class UserHandler:
    """Business logic layer for user operations."""

    def __init__(self, user_repo):
        self.user_repo = user_repo

    def create_user(self, name: str, email: str) -> dict:
        """Create a new user with validation."""
        if not name or not email:
            raise ValueError("name and email are required")

        return self.user_repo.create(name, email)

    def get_user(self, user_id: str) -> Optional[dict]:
        """Get a user by id."""
        if not user_id:
            raise ValueError("user_id is required")

        return self.user_repo.get_by_id(user_id)

    def get_all_users(self) -> list:
        """Get all users."""
        return self.user_repo.get_all()

    def update_user(self, user_id: str, name: Optional[str] = None, email: Optional[str] = None) -> Optional[dict]:
        """Update a user with validation."""
        if not user_id:
            raise ValueError("user_id is required")

        if not name and not email:
            raise ValueError("at least one of name or email must be provided")

        user = self.user_repo.get_by_id(user_id)
        if not user:
            return None

        return self.user_repo.update(user_id, name, email)

    def delete_user(self, user_id: str) -> bool:
        """Delete a user."""
        if not user_id:
            raise ValueError("user_id is required")

        return self.user_repo.delete(user_id)


