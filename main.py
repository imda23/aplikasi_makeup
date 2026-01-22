"""
Aplikasi Jasa Makeup
Entry point utama
"""
import sys
from PyQt5.QtWidgets import QApplication, QMessageBox
from config.settings import Settings
from config.database import Database
from views.login_view import LoginView
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main function"""
    # Ensure directories
    Settings.ensure_directories()
    logger.info("✅ Directories checked")
    
    # Test database connection
    logger.info("🔌 Testing database connection...")
    if not Database.test_connection():
        QMessageBox.critical(
            None,
            "Database Error",
            "❌ Tidak dapat terhubung ke database!\n\n"
            "Pastikan:\n"
            "1. Laragon MySQL sudah running\n"
            "2. Database 'db_jasa_makeup' sudah dibuat\n"
            "3. File .env sudah dikonfigurasi dengan benar"
        )
        return
    
    logger.info("✅ Database connection OK")
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName(Settings.APP_NAME)
    
    # Show login
    login = LoginView()
    login.show()
    
    # Run
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()