# ============================================
"""Authentication service"""
from config.database import Database
from utils.password_helper import PasswordHelper
from utils.session_manager import SessionManager, User
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class AuthService:
    @staticmethod
    def login(username: str, password: str) -> Tuple[bool, str, Optional[User]]:
        try:
            query = "SELECT * FROM user WHERE username = %s"
            result = Database.execute_query(query, (username,), fetch=True)
            
            if not result:
                return False, "Username atau password salah", None
            
            user_data = result[0]
            
            if not PasswordHelper.verify_password(password, user_data['password']):
                return False, "Username atau password salah", None
            
            user = User(
                id_user=user_data['id_user'],
                nama_user=user_data['nama_user'],
                username=user_data['username'],
                role=user_data['role']
            )
            
            SessionManager.login(user)
            logger.info(f"✅ User {username} logged in")
            return True, "Login berhasil", user
            
        except Exception as e:
            logger.error(f"❌ Login error: {e}")
            return False, "Terjadi kesalahan sistem", None
    
    @staticmethod
    def logout():
        SessionManager.logout()