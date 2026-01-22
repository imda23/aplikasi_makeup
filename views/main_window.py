"""
Main window dengan sidebar navigation
"""
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from ui.generated.ui_dashboard import Ui_MainWindow
from utils.session_manager import SessionManager
from services.dashboard_service import DashboardService
from utils.formatters import Formatters
import logging

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # Services
        self.dashboard_service = DashboardService()
        
        # Initialize
        self.init_ui()
        self.connect_signals()
        self.load_dashboard()
    
    def init_ui(self):
        """Initialize UI"""
        # Set user info
        user = SessionManager.get_current_user()
        if user:
            self.ui.lblUsername.setText(f"👤 {user.nama_user}")
    
    def connect_signals(self):
        """Connect button signals"""
        # Logout
        self.ui.btnLogout.clicked.connect(self.handle_logout)
        
        # Navigation
        self.ui.btnDashboard.clicked.connect(self.show_dashboard)
        self.ui.btnPelanggan.clicked.connect(self.go_pelanggan)
        self.ui.btnLayanan.clicked.connect(self.go_layanan)
        self.ui.btnJadwal.clicked.connect(self.go_jadwal)
        self.ui.btnTransaksi.clicked.connect(self.go_transaksi)
        self.ui.btnPembayaran.clicked.connect(self.go_pembayaran)
    
    def go_pelanggan(self):
        """Go to pelanggan view"""
        from views.pelanggan_view import PelangganView
        self.pelanggan_view = PelangganView()
        self.pelanggan_view.show()
        self.close()

    def go_layanan(self):
        """Go to layanan view"""
        from views.layanan_view import LayananView
        self.layanan_view = LayananView()
        self.layanan_view.show()
        self.close()

    def go_jadwal(self):
        """Go to jadwal view"""
        from views.jadwal_view import JadwalView
        self.jadwal_view = JadwalView()
        self.jadwal_view.show()
        self.close()

    def go_transaksi(self):
        """Go to transaksi view"""
        from views.transaksi_view import TransaksiView
        self.transaksi_view = TransaksiView()
        self.transaksi_view.show()
        self.close()

    def go_pembayaran(self):
        """Go to pembayaran view"""
        from views.pembayaran_view import PembayaranView
        self.pembayaran_view = PembayaranView()
        self.pembayaran_view.show()
        self.close()
    
    def show_temp_message(self, module_name):
        """Temporary message for modules not yet implemented"""
        QMessageBox.information(
            self,
            "Coming Soon",
            f"Modul {module_name} akan segera hadir!\n\n"
            f"Untuk saat ini, silakan lihat dashboard."
        )
    
    def show_dashboard(self):
        """Show dashboard (refresh)"""
        self.load_dashboard()
    
    def load_dashboard(self):
        """Load dashboard data"""
        try:
            # Get statistics
            stats = self.dashboard_service.get_statistics()
            
            # Update labels
            self.ui.lblStatValue1.setText(str(stats['total_pelanggan']))
            self.ui.lblStatValue2.setText(str(stats['transaksi_bulan_ini']))
            
            # Format pendapatan
            pendapatan = stats['pendapatan_hari_ini']
            if pendapatan >= 1000000:
                formatted = f"Rp {pendapatan/1000000:.1f} Jt"
            else:
                formatted = Formatters.format_currency(pendapatan)
            self.ui.lblStatValue3.setText(formatted)
            
            self.ui.lblStatValue4.setText(str(stats['jadwal_hari_ini']))
            
            # Load jadwal hari ini
            self.load_jadwal_today()
            
        except Exception as e:
            logger.error(f"Error loading dashboard: {e}")
            QMessageBox.critical(self, "Error", "Gagal memuat dashboard")
    
    def load_jadwal_today(self):
        """Load jadwal hari ini ke table"""
        try:
            jadwal_list = self.dashboard_service.get_jadwal_hari_ini()
            
            # Clear table
            self.ui.tableJadwalDashboard.setRowCount(0)
            
            # Populate table
            for jadwal in jadwal_list:
                row = self.ui.tableJadwalDashboard.rowCount()
                self.ui.tableJadwalDashboard.insertRow(row)
                
                # Waktu
                waktu = f"{Formatters.format_time(jadwal['jam_mulai'])} - {Formatters.format_time(jadwal['jam_selesai'])}"
                self.ui.tableJadwalDashboard.setItem(row, 0, self.create_table_item(waktu))
                
                # Pelanggan
                self.ui.tableJadwalDashboard.setItem(row, 1, self.create_table_item(jadwal['nama_pelanggan']))
                
                # Layanan (temporary - nanti ambil dari detail)
                self.ui.tableJadwalDashboard.setItem(row, 2, self.create_table_item("-"))
                
                # Status
                self.ui.tableJadwalDashboard.setItem(row, 3, self.create_table_item(jadwal['status']))
            
        except Exception as e:
            logger.error(f"Error loading jadwal: {e}")
    
    def create_table_item(self, text):
        """Create table widget item"""
        from PyQt5.QtWidgets import QTableWidgetItem
        from PyQt5.QtCore import Qt
        item = QTableWidgetItem(str(text))
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Read only
        return item
    
    def handle_logout(self):
        """Handle logout"""
        reply = QMessageBox.question(
            self,
            'Konfirmasi Logout',
            'Apakah Anda yakin ingin keluar?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            from services.auth_service import AuthService
            from views.login_view import LoginView
            
            AuthService.logout()
            
            # Show login
            login = LoginView()
            login.show()
            
            # Close main window
            self.close()
