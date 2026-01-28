"""
RBAC Decorator untuk proteksi akses
"""
from functools import wraps
from PyQt5.QtWidgets import QMessageBox
from utils.session_manager import SessionManager
import logging

logger = logging.getLogger(__name__)


def require_role(*allowed_roles):
    """
    Decorator untuk membatasi akses berdasarkan role
    Compatible dengan PyQt5 signals
    
    Usage:
        @require_role('admin', 'kasir')
        def some_function(self):
            pass
    
    Args:
        *allowed_roles: Variable number of role strings
    
    Returns:
        Decorator function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):  # ✅ PENTING: Terima semua args & kwargs
            # args[0] adalah self (instance)
            # args[1:] adalah parameter dari signal PyQt5 (checked, dll)
            
            user = SessionManager.get_current_user()
            
            # Log access attempt
            func_name = func.__name__
            username = user.username if user else 'unknown'
            user_role = user.role if user else 'N/A'
            
            logger.info(
                f"Access attempt: {func_name} by {username} ({user_role})"
            )
            
            # Check if user is logged in
            if not user:
                logger.warning(f"Unauthorized access to {func_name}")
                QMessageBox.warning(
                    None,
                    "Akses Ditolak",
                    "Anda harus login terlebih dahulu"
                )
                return None
            
            # Check if user has required role
            if user.role not in allowed_roles:
                logger.warning(
                    f"Permission denied: {username} ({user_role}) "
                    f"tried to access {func_name} (requires: {allowed_roles})"
                )
                
                # Format role names untuk display
                allowed_names = [role.replace('_', ' ').title() for role in allowed_roles]
                
                QMessageBox.warning(
                    None,
                    "Akses Ditolak",
                    f"Fitur ini hanya untuk: {', '.join(allowed_names)}\n\n"
                    f"Role Anda: {user_role.replace('_', ' ').title()}"
                )
                return None
            
            # Access granted - call original function
            logger.info(f"Access granted: {username} → {func_name}")
            
            # ✅ PENTING: Forward semua args & kwargs ke function asli
            return func(*args, **kwargs)
        
        return wrapper
    return decorator