"""
RBAC Helper untuk validasi di service layer
"""
from utils.session_manager import SessionManager
import logging

logger = logging.getLogger(__name__)


class RBACHelper:
    """Helper class untuk RBAC operations"""
    
    @staticmethod
    def check_permission(allowed_roles: list, operation: str = "") -> bool:
        """
        Check if current user has permission
        
        Args:
            allowed_roles: List of allowed roles
            operation: Operation name for logging
            
        Returns:
            bool: True if allowed, False otherwise
        """
        user = SessionManager.get_current_user()
        
        if not user:
            logger.warning(f"Unauthorized access attempt to {operation}")
            return False
        
        if user.role not in allowed_roles:
            logger.warning(
                f"Access denied for {user.username} ({user.role}) to {operation}"
            )
            return False
        
        logger.info(f"Permission granted: {user.username} → {operation}")
        return True
    
    @staticmethod
    def get_role_name(role: str) -> str:
        """
        Get human-readable role name
        
        Args:
            role: Role code (e.g., 'makeup_artist')
            
        Returns:
            str: Human-readable name (e.g., 'Makeup Artist')
        """
        role_names = {
            'admin': 'Administrator',
            'makeup_artist': 'Makeup Artist',
            'kasir': 'Kasir',
            'owner': 'Owner'
        }
        return role_names.get(role, role.replace('_', ' ').title())