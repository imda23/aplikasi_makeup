"""
Helper functions untuk password hashing dan verification
"""
import bcrypt
import logging

logger = logging.getLogger(__name__)


class PasswordHelper:
    """Helper class untuk password operations"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash password menggunakan bcrypt
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password string
        """
        try:
            salt = bcrypt.gensalt(rounds=12)
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            return hashed.decode('utf-8')
        except Exception as e:
            logger.error(f"Error hashing password: {e}")
            raise
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """
        Verify password against hash
        
        Args:
            password: Plain text password
            hashed: Hashed password from database
            
        Returns:
            True if password matches, False otherwise
        """
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                hashed.encode('utf-8')
            )
        except Exception as e:
            logger.error(f"Error verifying password: {e}")
            return False