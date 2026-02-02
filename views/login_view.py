"""
Login window
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QMessageBox, QApplication)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from services.auth_service import AuthService
from utils.rbac_helper import RBACHelper
from views.main_window import MainWindow
import logging

logger = logging.getLogger(__name__)


class LoginView(QWidget):
    """Login window"""
    
    def __init__(self):
        super().__init__()
        self.main_window = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("Login - Aplikasi Jasa Makeup")
        self.setFixedSize(450, 600)
        
        # Set background color
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
            }
        """)
        
        # Center window
        self.center_window()
        
        # Main Layout
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # ========================================
        # Logo/Icon Area (Optional - bisa tambah logo)
        # ========================================
        logo_label = QLabel("💄")
        logo_label.setAlignment(Qt.AlignCenter)
        logo_font = QFont()
        logo_font.setPointSize(42)  
        logo_label.setFont(logo_font)
        layout.addWidget(logo_label)
        
        # ========================================
        # Title
        # ========================================
        title = QLabel("MAKEUP APP")
        title.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #E91E63; margin-bottom: 5px;")
        layout.addWidget(title)
        
        # ========================================
        # Subtitle
        # ========================================
        subtitle = QLabel("Silakan Login")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("""
            color: #666; 
            font-size: 14pt;
            margin-bottom: 16px;
        """)
        layout.addWidget(subtitle)
        
        # ========================================
        # Username Field
        # ========================================
        username_label = QLabel("Username")
        username_label.setStyleSheet("color: #333; font-size: 10pt; font-weight: bold;")
        layout.addWidget(username_label)
        
        self.txt_username = QLineEdit()
        self.txt_username.setPlaceholderText("Masukkan username")
        self.txt_username.setMinimumHeight(45)  # ✅ Tinggi lebih besar
        self.txt_username.setStyleSheet("""
            QLineEdit {
                border: 2px solid #ddd;
                border-radius: 8px;
                padding: 10px 15px;
                font-size: 11pt;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #E91E63;
            }
        """)
        layout.addWidget(self.txt_username)
        
        # ========================================
        # Password Field
        # ========================================
        password_label = QLabel("Password")
        password_label.setStyleSheet("color: #333; font-size: 10pt; font-weight: bold; margin-top: 10px;")
        layout.addWidget(password_label)
        
        self.txt_password = QLineEdit()
        self.txt_password.setPlaceholderText("Masukkan password")
        self.txt_password.setMinimumHeight(45)  # ✅ Tinggi lebih besar
        self.txt_password.setEchoMode(QLineEdit.Password)
        self.txt_password.setStyleSheet("""
            QLineEdit {
                border: 2px solid #ddd;
                border-radius: 8px;
                padding: 10px 15px;
                font-size: 11pt;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #E91E63;
            }
        """)
        layout.addWidget(self.txt_password)
        
        # ========================================
        # Login Button
        # ========================================
        self.btn_login = QPushButton("🔐 Login")
        self.btn_login.setMinimumHeight(55)  # ✅ Button lebih besar
        self.btn_login.setCursor(Qt.PointingHandCursor)  # ✅ Cursor pointer
        self.btn_login.setStyleSheet("""
            QPushButton {
                background-color: #E91E63;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14pt;
                font-weight: bold;
                margin-top: 20px;
            }
            QPushButton:hover {
                background-color: #C2185B;
            }
            QPushButton:pressed {
                background-color: #AD1457;
            }
            QPushButton:disabled {
                background-color: #ccc;
            }
        """)
        self.btn_login.clicked.connect(self.handle_login)
        layout.addWidget(self.btn_login)
        
        # ========================================
        # Info Text (Credential Helper)
        # ========================================
        info = QLabel("Gunakan: sinta_admin / 12345")
        info.setAlignment(Qt.AlignCenter)
        info.setWordWrap(True)
        info.setMinimumHeight(40)
        info.setStyleSheet("""
            color: #999; 
            font-size: 9pt; 
            margin-top: 15px;
            padding: 6px;
            background-color: #fff3cd;
            border: 1px solid #ffc107;
            border-radius: 5px;
        """)
        layout.addWidget(info)
        
        # ========================================
        # Footer space (untuk estetika)
        # ========================================
        footer = QLabel("")
        footer.setMinimumHeight(20)  # ✅ Tambah space di bawah
        layout.addWidget(footer)
        
        self.setLayout(layout)
        
        # Enter key shortcut
        self.txt_password.returnPressed.connect(self.handle_login)
        
        # Set focus to username
        self.txt_username.setFocus()
    
    def center_window(self):
        """Center window on screen"""
        screen = QApplication.desktop().screenGeometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
    
    def handle_login(self):
        """Handle login button click"""
        username = self.txt_username.text().strip()
        password = self.txt_password.text()
        
        # Validation
        if not username:
            QMessageBox.warning(self, "Validasi", "Username wajib diisi")
            self.txt_username.setFocus()
            return
        
        if not password:
            QMessageBox.warning(self, "Validasi", "Password wajib diisi")
            self.txt_password.setFocus()
            return
        
        # Show loading
        self.btn_login.setEnabled(False)
        self.btn_login.setText("⏳ Loading...")
        QApplication.processEvents()
        
        # Login
        success, message, user = AuthService.login(username, password)
        
        # Restore button
        self.btn_login.setEnabled(True)
        self.btn_login.setText("🔐 Login")
        
        if success:
            logger.info(f"Login successful: {username}")
            
            QMessageBox.information(
                self,
                "Login Berhasil",
                f"Selamat datang, {user.nama_user}!\n\n"
                f"Role: {RBACHelper.get_role_name(user.role)}"
            )
            
            # Open main window
            self.main_window = MainWindow()
            self.main_window.showMaximized()
            
            # Close login
            self.close()
        else:
            QMessageBox.warning(self, "Login Gagal", message)
            self.txt_password.clear()
            self.txt_username.setFocus()