"""Transaksi View - Display only (simplified)"""
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QTableWidgetItem, QApplication
from PyQt5.QtCore import Qt
from ui.generated.ui_form_transaksi import Ui_MainWindow
from services.transaksi_service import TransaksiService
from services.auth_service import AuthService
from utils.session_manager import SessionManager
from utils.formatters import Formatters

class TransaksiView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.transaksi_service = TransaksiService()
        self.init_ui()
        self.connect_signals()
        self.load_data()
    
    def init_ui(self):
        user = SessionManager.get_current_user()
        if user:
            self.ui.lblUsername.setText(f"👤 {user.nama_user}")
    
    def connect_signals(self):
        self.ui.btnDashboard.clicked.connect(self.go_dashboard)
        self.ui.btnPelanggan.clicked.connect(self.go_pelanggan)
        self.ui.btnLayanan.clicked.connect(self.go_layanan)
        self.ui.btnJadwal.clicked.connect(self.go_jadwal)
        self.ui.btnPembayaran.clicked.connect(self.go_pembayaran)
        self.ui.btnLogout.clicked.connect(self.handle_logout)
    
    def load_data(self):
        try:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            data = self.transaksi_service.get_all()
            self.ui.tableHistoryTransaksi.setRowCount(0)
            
            for row_idx, item in enumerate(data):
                self.ui.tableHistoryTransaksi.insertRow(row_idx)
                self.ui.tableHistoryTransaksi.setItem(row_idx, 0, self.create_item(item['id_transaksi']))
                self.ui.tableHistoryTransaksi.setItem(row_idx, 1, self.create_item(Formatters.format_date(item['tanggal_transaksi'])))
                self.ui.tableHistoryTransaksi.setItem(row_idx, 2, self.create_item(item['nama_pelanggan']))
                self.ui.tableHistoryTransaksi.setItem(row_idx, 3, self.create_item(Formatters.format_currency(item['total'])))
                self.ui.tableHistoryTransaksi.setItem(row_idx, 4, self.create_item("Selesai"))
            
            QApplication.restoreOverrideCursor()
        except Exception as e:
            QApplication.restoreOverrideCursor()
            QMessageBox.critical(self, "Error", "Gagal memuat data")
    
    def create_item(self, text):
        item = QTableWidgetItem(str(text))
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
        return item
    
    def go_dashboard(self):
        from views.main_window import MainWindow
        self.main_window = MainWindow()
        self.main_window.show()
        self.close()
    
    def go_pelanggan(self):
        from views.pelanggan_view import PelangganView
        self.pelanggan_view = PelangganView()
        self.pelanggan_view.show()
        self.close()
    
    def go_layanan(self):
        from views.layanan_view import LayananView
        self.layanan_view = LayananView()
        self.layanan_view.show()
        self.close()
    
    def go_jadwal(self):
        from views.jadwal_view import JadwalView
        self.jadwal_view = JadwalView()
        self.jadwal_view.show()
        self.close()
    
    def go_pembayaran(self):
        from views.pembayaran_view import PembayaranView
        self.pembayaran_view = PembayaranView()
        self.pembayaran_view.show()
        self.close()
    
    def handle_logout(self):
        reply = QMessageBox.question(self, 'Konfirmasi Logout', 'Keluar?', QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            AuthService.logout()
            from views.login_view import LoginView
            login = LoginView()
            login.show()
            self.close()