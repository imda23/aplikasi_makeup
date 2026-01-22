"""
Pelanggan View dengan CRUD lengkap
"""
from PyQt5.QtWidgets import (QMainWindow, QMessageBox, QTableWidgetItem, 
                             QPushButton, QHBoxLayout, QWidget, QApplication)
from PyQt5.QtCore import Qt
from ui.generated.ui_form_pelanggan import Ui_MainWindow
from services.pelanggan_service import PelangganService
from services.auth_service import AuthService
from utils.validators import Validators
from utils.session_manager import SessionManager
import logging

logger = logging.getLogger(__name__)


class PelangganView(QMainWindow):
    """View untuk manage pelanggan"""
    
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # Services
        self.pelanggan_service = PelangganService()
        
        # State
        self.current_mode = "create"  # "create" atau "update"
        self.current_id = None
        
        # Initialize
        self.init_ui()
        self.connect_signals()
        self.load_data()
    
    def init_ui(self):
        """Initialize UI"""
        # Hide form initially
        self.ui.groupFormPelanggan.setVisible(False)
        
        # Set user info
        user = SessionManager.get_current_user()
        if user:
            self.ui.lblUsername.setText(f"👤 {user.nama_user}")
        
        # Setup table
        self.ui.tablePelanggan.setColumnWidth(0, 50)   # ID
        self.ui.tablePelanggan.setColumnWidth(1, 200)  # Nama
        self.ui.tablePelanggan.setColumnWidth(2, 150)  # No HP
        self.ui.tablePelanggan.setColumnWidth(3, 250)  # Alamat
        self.ui.tablePelanggan.setColumnWidth(4, 180)  # Aksi
    
    def connect_signals(self):
        """Connect signals"""
        # Navigation
        self.ui.btnDashboard.clicked.connect(self.go_dashboard)
        self.ui.btnPelanggan.clicked.connect(lambda: self.load_data())
        self.ui.btnLayanan.clicked.connect(self.go_layanan)
        self.ui.btnJadwal.clicked.connect(self.go_jadwal)
        self.ui.btnTransaksi.clicked.connect(self.go_transaksi)
        self.ui.btnPembayaran.clicked.connect(self.go_pembayaran)
        self.ui.btnLogout.clicked.connect(self.handle_logout)
        
        # Search
        self.ui.txtSearchPelanggan.textChanged.connect(self.search_pelanggan)
        
        # Buttons
        self.ui.btnTambahPelanggan.clicked.connect(self.show_form_create)
        self.ui.btnSimpanPelanggan.clicked.connect(self.save_pelanggan)
        self.ui.btnBatalPelanggan.clicked.connect(self.cancel_form)
    
    # ============================================
    # CRUD Operations
    # ============================================
    
    def load_data(self):
        """Load all data"""
        try:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            
            data = self.pelanggan_service.get_all()
            
            self.ui.tablePelanggan.setRowCount(0)
            
            for row_idx, item in enumerate(data):
                self.ui.tablePelanggan.insertRow(row_idx)
                
                # ID
                self.ui.tablePelanggan.setItem(row_idx, 0, self.create_item(item['id_pelanggan']))
                
                # Nama
                self.ui.tablePelanggan.setItem(row_idx, 1, self.create_item(item['nama']))
                
                # No HP
                self.ui.tablePelanggan.setItem(row_idx, 2, self.create_item(item['no_hp']))
                
                # Alamat
                self.ui.tablePelanggan.setItem(row_idx, 3, self.create_item(item['alamat']))
                
                # Action buttons
                self.add_action_buttons(row_idx, item['id_pelanggan'])
            
            QApplication.restoreOverrideCursor()
            
        except Exception as e:
            QApplication.restoreOverrideCursor()
            logger.error(f"Error loading data: {e}")
            QMessageBox.critical(self, "Error", "Gagal memuat data")
    
    def search_pelanggan(self):
        """Search pelanggan"""
        keyword = self.ui.txtSearchPelanggan.text().strip()
        
        if not keyword:
            self.load_data()
            return
        
        try:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            
            data = self.pelanggan_service.search(keyword)
            
            self.ui.tablePelanggan.setRowCount(0)
            
            for row_idx, item in enumerate(data):
                self.ui.tablePelanggan.insertRow(row_idx)
                self.ui.tablePelanggan.setItem(row_idx, 0, self.create_item(item['id_pelanggan']))
                self.ui.tablePelanggan.setItem(row_idx, 1, self.create_item(item['nama']))
                self.ui.tablePelanggan.setItem(row_idx, 2, self.create_item(item['no_hp']))
                self.ui.tablePelanggan.setItem(row_idx, 3, self.create_item(item['alamat']))
                self.add_action_buttons(row_idx, item['id_pelanggan'])
            
            QApplication.restoreOverrideCursor()
            
        except Exception as e:
            QApplication.restoreOverrideCursor()
            logger.error(f"Error searching: {e}")
    
    def show_form_create(self):
        """Show form for create"""
        self.current_mode = "create"
        self.current_id = None
        self.clear_form()
        self.ui.groupFormPelanggan.setVisible(True)
        self.ui.groupFormPelanggan.setTitle("📝 Form Tambah Pelanggan")
        self.ui.txtNamaPelanggan.setFocus()
    
    def show_form_update(self, id_pelanggan):
        """Show form for update"""
        try:
            data = self.pelanggan_service.get_by_id(id_pelanggan)
            
            if not data:
                QMessageBox.warning(self, "Error", "Data tidak ditemukan")
                return
            
            self.current_mode = "update"
            self.current_id = id_pelanggan
            
            # Fill form
            self.ui.txtNamaPelanggan.setText(data['nama'])
            self.ui.txtNoHPPelanggan.setText(data['no_hp'])
            self.ui.txtAlamatPelanggan.setPlainText(data['alamat'])
            
            self.ui.groupFormPelanggan.setVisible(True)
            self.ui.groupFormPelanggan.setTitle("📝 Form Edit Pelanggan")
            self.ui.txtNamaPelanggan.setFocus()
            
        except Exception as e:
            logger.error(f"Error loading for update: {e}")
            QMessageBox.critical(self, "Error", "Gagal memuat data")
    
    def save_pelanggan(self):
        """Save pelanggan"""
        # Get data
        nama = self.ui.txtNamaPelanggan.text().strip()
        no_hp = self.ui.txtNoHPPelanggan.text().strip()
        alamat = self.ui.txtAlamatPelanggan.toPlainText().strip()
        
        # Validate
        if not self.validate_form(nama, no_hp, alamat):
            return
        
        try:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            
            if self.current_mode == "create":
                success, message = self.pelanggan_service.create(nama, no_hp, alamat)
            else:
                success, message = self.pelanggan_service.update(self.current_id, nama, no_hp, alamat)
            
            QApplication.restoreOverrideCursor()
            
            if success:
                QMessageBox.information(self, "Sukses", message)
                self.load_data()
                self.cancel_form()
            else:
                QMessageBox.warning(self, "Gagal", message)
                
        except Exception as e:
            QApplication.restoreOverrideCursor()
            logger.error(f"Error saving: {e}")
            QMessageBox.critical(self, "Error", "Terjadi kesalahan sistem")
    
    def delete_pelanggan(self, id_pelanggan):
        """Delete pelanggan"""
        reply = QMessageBox.question(
            self, 'Konfirmasi Hapus',
            'Apakah Anda yakin ingin menghapus pelanggan ini?\n\n'
            'Data yang sudah dihapus tidak dapat dikembalikan.',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.No:
            return
        
        try:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            
            success, message = self.pelanggan_service.delete(id_pelanggan)
            
            QApplication.restoreOverrideCursor()
            
            if success:
                QMessageBox.information(self, "Sukses", message)
                self.load_data()
            else:
                QMessageBox.warning(self, "Gagal", message)
                
        except Exception as e:
            QApplication.restoreOverrideCursor()
            logger.error(f"Error deleting: {e}")
            QMessageBox.critical(self, "Error", "Terjadi kesalahan sistem")
    
    # ============================================
    # Helper Methods
    # ============================================
    
    def validate_form(self, nama, no_hp, alamat):
        """Validate form"""
        # Nama
        is_valid, error = Validators.validate_required(nama, "Nama")
        if not is_valid:
            QMessageBox.warning(self, "Validasi", error)
            self.ui.txtNamaPelanggan.setFocus()
            return False
        
        # No HP
        is_valid, error = Validators.validate_required(no_hp, "No HP")
        if not is_valid:
            QMessageBox.warning(self, "Validasi", error)
            self.ui.txtNoHPPelanggan.setFocus()
            return False
        
        is_valid, error = Validators.validate_phone(no_hp)
        if not is_valid:
            QMessageBox.warning(self, "Validasi", error)
            self.ui.txtNoHPPelanggan.setFocus()
            return False
        
        # Alamat
        is_valid, error = Validators.validate_required(alamat, "Alamat")
        if not is_valid:
            QMessageBox.warning(self, "Validasi", error)
            self.ui.txtAlamatPelanggan.setFocus()
            return False
        
        return True
    
    def add_action_buttons(self, row, id_pelanggan):
        """Add action buttons"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 0, 5, 0)
        
        # Edit button
        btn_edit = QPushButton("✏️ Edit")
        btn_edit.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
        """)
        btn_edit.clicked.connect(lambda: self.show_form_update(id_pelanggan))
        
        # Delete button
        btn_delete = QPushButton("🗑️ Hapus")
        btn_delete.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        btn_delete.clicked.connect(lambda: self.delete_pelanggan(id_pelanggan))
        
        layout.addWidget(btn_edit)
        layout.addWidget(btn_delete)
        layout.addStretch()
        
        self.ui.tablePelanggan.setCellWidget(row, 4, widget)
    
    def create_item(self, text):
        """Create table item"""
        item = QTableWidgetItem(str(text))
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
        return item
    
    def clear_form(self):
        """Clear form"""
        self.ui.txtNamaPelanggan.clear()
        self.ui.txtNoHPPelanggan.clear()
        self.ui.txtAlamatPelanggan.clear()
    
    def cancel_form(self):
        """Cancel form"""
        self.clear_form()
        self.ui.groupFormPelanggan.setVisible(False)
        self.current_mode = "create"
        self.current_id = None
    
    # ============================================
    # Navigation
    # ============================================
    
    def go_dashboard(self):
        from views.main_window import MainWindow
        self.main_window = MainWindow()
        self.main_window.show()
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
    
    def go_transaksi(self):
        from views.transaksi_view import TransaksiView
        self.transaksi_view = TransaksiView()
        self.transaksi_view.show()
        self.close()
    
    def go_pembayaran(self):
        from views.pembayaran_view import PembayaranView
        self.pembayaran_view = PembayaranView()
        self.pembayaran_view.show()
        self.close()
    
    def handle_logout(self):
        """Handle logout"""
        reply = QMessageBox.question(
            self, 'Konfirmasi Logout',
            'Apakah Anda yakin ingin keluar?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            AuthService.logout()
            from views.login_view import LoginView
            login = LoginView()
            login.show()
            self.close()