"""
Session management untuk user authentication
"""
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class User:
    """User model untuk session"""
    def __init__(self, id_user: int, nama_user: str, username: str, role: str):
        self.id_user = id_user
        self.nama_user = nama_user
        self.username = username
        self.role = role


class SessionManager:
    """Singleton class untuk manage user session"""
    
    _instance = None
    _current_user: Optional[User] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SessionManager, cls).__new__(cls)
        return cls._instance
    
    @classmethod
    def login(cls, user: User):
        """Set current user session"""
        cls._current_user = user
        logger.info(f"User logged in: {user.username} ({user.role})")
    
    @classmethod
    def logout(cls):
        """Clear current user session"""
        if cls._current_user:
            logger.info(f"User logged out: {cls._current_user.username}")
        cls._current_user = None
    
    @classmethod
    def get_current_user(cls) -> Optional[User]:
        """Get current logged in user"""
        return cls._current_user
    
    @classmethod
    def is_authenticated(cls) -> bool:
        """Check if user is logged in"""
        return cls._current_user is not None
    
    @classmethod
    def has_role(cls, role: str) -> bool:
        """Check if current user has specific role"""
        if not cls.is_authenticated():
            return False
        return cls._current_user.role == role
    
    @classmethod
    def has_any_role(cls, roles: list) -> bool:
        """Check if current user has any of the specified roles"""
        if not cls.is_authenticated():
            return False
        return cls._current_user.role in roles