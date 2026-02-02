"""
Layanan View dengan CRUD lengkap
"""
from PyQt5.QtWidgets import (QMainWindow, QMessageBox, QTableWidgetItem, 
                             QPushButton, QHBoxLayout, QWidget, QApplication,
                             QInputDialog)
from PyQt5.QtCore import Qt, QTime
from ui.generated.ui_form_layanan import Ui_MainWindow
from services.layanan_service import LayananService
from utils.rbac_decorator import require_role
from utils.rbac_helper import RBACHelper
from services.auth_service import AuthService
from utils.validators import Validators
from utils.session_manager import SessionManager
from utils.formatters import Formatters
import logging

logger = logging.getLogger(__name__)


class LayananView(QMainWindow):
    """View untuk manage layanan"""
    
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # Services
        self.layanan_service = LayananService()
        
        # State
        self.current_mode = "create"  # "create" atau "update"
        self.current_id = None
        self.current_kategori_id = None
        
        # Initialize
        self.init_ui()
        self.connect_signals()
        self.load_data()
        self.load_kategori()
        self.load_kategori_combo()
    
    def init_ui(self):
        """Initialize UI"""
        # Hide form initially
        self.ui.groupFormLayanan.setVisible(False)
        
        # Set user info
        user = SessionManager.get_current_user()
        if user:
            self.ui.lblUsername.setText(
                f"👤 {user.nama_user} ({RBACHelper.get_role_name(user.role)})"
            )
            # Setup RBAC UI
            self.setup_rbac_ui(user.role)
            self.setup_menu_visibility(user.role)
            
        # Setup table layanan
        self.ui.tableLayanan.setColumnWidth(0, 50)   # ID
        self.ui.tableLayanan.setColumnWidth(1, 200)  # Nama
        self.ui.tableLayanan.setColumnWidth(2, 150)  # Kategori
        self.ui.tableLayanan.setColumnWidth(3, 120)  # Harga
        self.ui.tableLayanan.setColumnWidth(4, 100)  # Durasi
        self.ui.tableLayanan.setColumnWidth(5, 180)  # Aksi
        
        # Setup table kategori
        self.ui.tableKategori.setColumnWidth(0, 100)  # ID
        self.ui.tableKategori.setColumnWidth(1, 400)  # Nama
        self.ui.tableKategori.setColumnWidth(2, 200)  # Aksi
    
    def setup_rbac_ui(self, role):
        """Setup UI based on user role"""
        if role == 'owner':
            # Owner: Read-only
            self.ui.btnTambahLayanan.setVisible(False)
            self.ui.btnTambahKategori.setVisible(False)
            self.ui.groupFormLayanan.setVisible(False)
    
    def setup_menu_visibility(self, role):
        """
        Setup sidebar menu visibility based on user role
        
        Args:
            role: User role string
        """
        if role == 'makeup_artist':
            # MUA: Hanya Dashboard dan Jadwal
            self.ui.btnPelanggan.setVisible(False)
            self.ui.btnLayanan.setVisible(False)
            self.ui.btnTransaksi.setVisible(False)
            self.ui.btnPembayaran.setVisible(False)
            
        elif role == 'kasir':
            # Kasir: Dashboard, Pelanggan, Transaksi, Pembayaran
            self.ui.btnLayanan.setVisible(False)
            self.ui.btnJadwal.setVisible(False)
            
        elif role == 'owner':
            # Owner: Semua menu visible (read-only di-handle di setup_rbac_ui)
            pass
            
        elif role == 'admin':
            # Admin: Full access - semua visible
            pass
    
    def connect_signals(self):
        """Connect signals"""
        # Navigation
        self.ui.btnDashboard.clicked.connect(self.go_dashboard)
        self.ui.btnPelanggan.clicked.connect(self.go_pelanggan)
        self.ui.btnLayanan.clicked.connect(lambda: self.load_data())
        self.ui.btnJadwal.clicked.connect(self.go_jadwal)
        self.ui.btnTransaksi.clicked.connect(self.go_transaksi)
        self.ui.btnPembayaran.clicked.connect(self.go_pembayaran)
        self.ui.btnLogout.clicked.connect(self.handle_logout)
        
        # Search Layanan
        self.ui.txtSearchLayanan.textChanged.connect(self.search_layanan)
        
        # Buttons Layanan
        self.ui.btnTambahLayanan.clicked.connect(self.show_form_create)
        self.ui.btnSimpanLayanan.clicked.connect(self.save_layanan)
        self.ui.btnBatalLayanan.clicked.connect(self.cancel_form)
        
        # Search Kategori
        self.ui.txtSearchKategori.textChanged.connect(self.search_kategori)
        
        # Buttons Kategori
        self.ui.btnTambahKategori.clicked.connect(self.create_kategori)
    
    # ============================================
    # CRUD Layanan
    # ============================================
    
    def load_data(self):
        """Load all layanan"""
        try:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            
            data = self.layanan_service.get_all()
            
            self.ui.tableLayanan.setRowCount(0)
            
            for row_idx, item in enumerate(data):
                self.ui.tableLayanan.insertRow(row_idx)
                
                # ID
                self.ui.tableLayanan.setItem(row_idx, 0, self.create_item(item['id_layanan']))
                
                # Nama Layanan
                self.ui.tableLayanan.setItem(row_idx, 1, self.create_item(item['nama_layanan']))
                
                # Kategori
                self.ui.tableLayanan.setItem(row_idx, 2, self.create_item(item['nama_kategori']))
                
                # Harga
                self.ui.tableLayanan.setItem(row_idx, 3, self.create_item(Formatters.format_currency(item['harga'])))
                
                # Durasi
                self.ui.tableLayanan.setItem(row_idx, 4, self.create_item(Formatters.format_time(item['durasi'])))
                
                # Action buttons
                self.add_action_buttons_layanan(row_idx, item['id_layanan'])
            
            QApplication.restoreOverrideCursor()
            
        except Exception as e:
            QApplication.restoreOverrideCursor()
            logger.error(f"Error loading data: {e}")
            QMessageBox.critical(self, "Error", "Gagal memuat data")
    
    def search_layanan(self):
        """Search layanan"""
        keyword = self.ui.txtSearchLayanan.text().strip().lower()
        
        if not keyword:
            self.load_data()
            return
        
        try:
            # Filter table
            for row in range(self.ui.tableLayanan.rowCount()):
                show_row = False
                for col in range(self.ui.tableLayanan.columnCount() - 1):  # Exclude action column
                    item = self.ui.tableLayanan.item(row, col)
                    if item and keyword in item.text().lower():
                        show_row = True
                        break
                self.ui.tableLayanan.setRowHidden(row, not show_row)
            
        except Exception as e:
            logger.error(f"Error searching: {e}")
    
    @require_role('admin')
    def show_form_create(self, checked=False):
        """Show form for create layanan"""
        self.current_mode = "create"
        self.current_id = None
        self.clear_form_layanan()
        self.ui.groupFormLayanan.setVisible(True)
        self.ui.groupFormLayanan.setTitle("📝 Form Tambah Layanan")
        self.ui.txtNamaLayanan.setFocus()
    
    @require_role('admin')
    def show_form_update(self, id_layanan):
        """Show form for update layanan"""
        try:
            # Get layanan data
            data = self.layanan_service.get_all()
            layanan = next((item for item in data if item['id_layanan'] == id_layanan), None)
            
            if not layanan:
                QMessageBox.warning(self, "Error", "Data tidak ditemukan")
                return
            
            self.current_mode = "update"
            self.current_id = id_layanan
            
            # Fill form
            self.ui.txtNamaLayanan.setText(layanan['nama_layanan'])
            
            # Set kategori
            index = self.ui.cmbKategori.findData(layanan['id_kategori'])
            if index >= 0:
                self.ui.cmbKategori.setCurrentIndex(index)
            
            # Set harga
            self.ui.spinHarga.setValue(int(layanan['harga']))
            
            # Set durasi
            from datetime import datetime
            durasi_obj = datetime.strptime(str(layanan['durasi']), '%H:%M:%S').time()
            self.ui.timeDurasi.setTime(QTime(durasi_obj.hour, durasi_obj.minute))
            
            # Set deskripsi
            if layanan.get('deskripsi'):
                self.ui.txtDeskripsi.setPlainText(layanan['deskripsi'])
            
            self.ui.groupFormLayanan.setVisible(True)
            self.ui.groupFormLayanan.setTitle("📝 Form Edit Layanan")
            self.ui.txtNamaLayanan.setFocus()
            
        except Exception as e:
            logger.error(f"Error loading for update: {e}")
            QMessageBox.critical(self, "Error", "Gagal memuat data")
    
    @require_role('admin')
    def save_layanan(self,checked=False):
        """Save layanan"""
        # Get data
        nama = self.ui.txtNamaLayanan.text().strip()
        id_kategori = self.ui.cmbKategori.currentData()
        harga = self.ui.spinHarga.value()
        durasi = self.ui.timeDurasi.time().toString('HH:mm:ss')
        deskripsi = self.ui.txtDeskripsi.toPlainText().strip()
        
        # Validate
        if not self.validate_form_layanan(nama, id_kategori, harga):
            return
        
        try:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            
            from config.database import Database
            
            if self.current_mode == "create":
                query = """
                    INSERT INTO layanan (nama_layanan, id_kategori, harga, durasi, deskripsi) 
                    VALUES (%s, %s, %s, %s, %s)
                """
                Database.execute_query(query, (nama, id_kategori, harga, durasi, deskripsi))
                message = "Layanan berhasil ditambahkan"
            else:
                query = """
                    UPDATE layanan 
                    SET nama_layanan=%s, id_kategori=%s, harga=%s, durasi=%s, deskripsi=%s 
                    WHERE id_layanan=%s
                """
                Database.execute_query(query, (nama, id_kategori, harga, durasi, deskripsi, self.current_id))
                message = "Layanan berhasil diupdate"
            
            QApplication.restoreOverrideCursor()
            
            QMessageBox.information(self, "Sukses", message)
            self.load_data()
            self.cancel_form()
            
        except Exception as e:
            QApplication.restoreOverrideCursor()
            logger.error(f"Error saving: {e}")
            QMessageBox.critical(self, "Error", "Terjadi kesalahan sistem")
    
    @require_role('admin')
    def delete_layanan(self, id_layanan):
        """Delete layanan"""
        reply = QMessageBox.question(
            self, 'Konfirmasi Hapus',
            'Apakah Anda yakin ingin menghapus layanan ini?\n\n'
            'Data yang sudah dihapus tidak dapat dikembalikan.',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.No:
            return
        
        try:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            
            from config.database import Database
            
            # Check if used in transaksi
            check = "SELECT COUNT(*) as count FROM detail_transaksi WHERE id_layanan = %s"
            result = Database.execute_query(check, (id_layanan,), fetch=True)
            if result[0]['count'] > 0:
                QApplication.restoreOverrideCursor()
                QMessageBox.warning(self, "Gagal", "Layanan sudah digunakan dalam transaksi, tidak dapat dihapus")
                return
            
            query = "DELETE FROM layanan WHERE id_layanan = %s"
            Database.execute_query(query, (id_layanan,))
            
            QApplication.restoreOverrideCursor()
            
            QMessageBox.information(self, "Sukses", "Layanan berhasil dihapus")
            self.load_data()
            
        except Exception as e:
            QApplication.restoreOverrideCursor()
            logger.error(f"Error deleting: {e}")
            QMessageBox.critical(self, "Error", "Terjadi kesalahan sistem")
    
    # ============================================
    # CRUD Kategori
    # ============================================
    
    def load_kategori(self):
        """Load all kategori"""
        try:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            
            data = self.layanan_service.get_kategori_all()
            
            self.ui.tableKategori.setRowCount(0)
            
            for row_idx, item in enumerate(data):
                self.ui.tableKategori.insertRow(row_idx)
                
                # ID
                self.ui.tableKategori.setItem(row_idx, 0, self.create_item(item['id_kategori']))
                
                # Nama Kategori
                self.ui.tableKategori.setItem(row_idx, 1, self.create_item(item['nama_kategori']))
                
                # Action buttons
                self.add_action_buttons_kategori(row_idx, item['id_kategori'])
            
            QApplication.restoreOverrideCursor()
            
        except Exception as e:
            QApplication.restoreOverrideCursor()
            logger.error(f"Error loading kategori: {e}")
            QMessageBox.critical(self, "Error", "Gagal memuat data kategori")
    
    def load_kategori_combo(self):
        """Load kategori to combobox"""
        try:
            data = self.layanan_service.get_kategori_all()
            
            self.ui.cmbKategori.clear()
            
            for item in data:
                self.ui.cmbKategori.addItem(item['nama_kategori'], item['id_kategori'])
            
        except Exception as e:
            logger.error(f"Error loading kategori combo: {e}")
    
    def search_kategori(self):
        """Search kategori"""
        keyword = self.ui.txtSearchKategori.text().strip().lower()
        
        if not keyword:
            self.load_kategori()
            return
        
        try:
            # Filter table
            for row in range(self.ui.tableKategori.rowCount()):
                show_row = False
                for col in range(self.ui.tableKategori.columnCount() - 1):  # Exclude action column
                    item = self.ui.tableKategori.item(row, col)
                    if item and keyword in item.text().lower():
                        show_row = True
                        break
                self.ui.tableKategori.setRowHidden(row, not show_row)
            
        except Exception as e:
            logger.error(f"Error searching kategori: {e}")
    
    @require_role('admin')
    def create_kategori(self,checked=False):
        """Create new kategori using input dialog"""
        nama, ok = QInputDialog.getText(
            self, 
            'Tambah Kategori', 
            'Nama Kategori:',
            text=''
        )
        
        if ok and nama.strip():
            try:
                QApplication.setOverrideCursor(Qt.WaitCursor)
                
                from config.database import Database
                query = "INSERT INTO kategori_layanan (nama_kategori) VALUES (%s)"
                Database.execute_query(query, (nama.strip(),))
                
                QApplication.restoreOverrideCursor()
                
                QMessageBox.information(self, "Sukses", "Kategori berhasil ditambahkan")
                self.load_kategori()
                self.load_kategori_combo()
                
            except Exception as e:
                QApplication.restoreOverrideCursor()
                logger.error(f"Error creating kategori: {e}")
                QMessageBox.critical(self, "Error", "Gagal menambahkan kategori")
    
    @require_role('admin')
    def update_kategori(self, id_kategori):
        """Update kategori"""
        try:
            # Get current name
            data = self.layanan_service.get_kategori_all()
            kategori = next((item for item in data if item['id_kategori'] == id_kategori), None)
            
            if not kategori:
                QMessageBox.warning(self, "Error", "Data tidak ditemukan")
                return
            
            nama, ok = QInputDialog.getText(
                self, 
                'Edit Kategori', 
                'Nama Kategori:',
                text=kategori['nama_kategori']
            )
            
            if ok and nama.strip():
                QApplication.setOverrideCursor(Qt.WaitCursor)
                
                from config.database import Database
                query = "UPDATE kategori_layanan SET nama_kategori=%s WHERE id_kategori=%s"
                Database.execute_query(query, (nama.strip(), id_kategori))
                
                QApplication.restoreOverrideCursor()
                
                QMessageBox.information(self, "Sukses", "Kategori berhasil diupdate")
                self.load_kategori()
                self.load_kategori_combo()
            
        except Exception as e:
            QApplication.restoreOverrideCursor()
            logger.error(f"Error updating kategori: {e}")
            QMessageBox.critical(self, "Error", "Gagal mengupdate kategori")
    
    @require_role('admin')
    def delete_kategori(self, id_kategori):
        """Delete kategori"""
        reply = QMessageBox.question(
            self, 'Konfirmasi Hapus',
            'Apakah Anda yakin ingin menghapus kategori ini?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.No:
            return
        
        try:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            
            from config.database import Database
            
            # Check if used in layanan
            check = "SELECT COUNT(*) as count FROM layanan WHERE id_kategori = %s"
            result = Database.execute_query(check, (id_kategori,), fetch=True)
            if result[0]['count'] > 0:
                QApplication.restoreOverrideCursor()
                QMessageBox.warning(self, "Gagal", "Kategori sudah digunakan dalam layanan, tidak dapat dihapus")
                return
            
            query = "DELETE FROM kategori_layanan WHERE id_kategori = %s"
            Database.execute_query(query, (id_kategori,))
            
            QApplication.restoreOverrideCursor()
            
            QMessageBox.information(self, "Sukses", "Kategori berhasil dihapus")
            self.load_kategori()
            self.load_kategori_combo()
            
        except Exception as e:
            QApplication.restoreOverrideCursor()
            logger.error(f"Error deleting kategori: {e}")
            QMessageBox.critical(self, "Error", "Terjadi kesalahan sistem")
    
    # ============================================
    # Helper Methods
    # ============================================
    
    def validate_form_layanan(self, nama, id_kategori, harga):
        """Validate form layanan"""
        # Nama
        is_valid, error = Validators.validate_required(nama, "Nama Layanan")
        if not is_valid:
            QMessageBox.warning(self, "Validasi", error)
            self.ui.txtNamaLayanan.setFocus()
            return False
        
        # Kategori
        if id_kategori is None:
            QMessageBox.warning(self, "Validasi", "Kategori wajib dipilih")
            self.ui.cmbKategori.setFocus()
            return False
        
        # Harga
        is_valid, error = Validators.validate_positive_number(harga, "Harga")
        if not is_valid:
            QMessageBox.warning(self, "Validasi", error)
            self.ui.spinHarga.setFocus()
            return False
        
        return True
    
    def add_action_buttons_layanan(self, row, id_layanan):
        """Add action buttons for layanan"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 0, 5, 0)
        
        user = SessionManager.get_current_user()
        
        if user and user.role == 'admin':
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
            btn_edit.clicked.connect(lambda: self.show_form_update(id_layanan))
            
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
            btn_delete.clicked.connect(lambda: self.delete_layanan(id_layanan))
            
            layout.addWidget(btn_edit)
            layout.addWidget(btn_delete)
        
        layout.addStretch()
        
        self.ui.tableLayanan.setCellWidget(row, 5, widget)
    
    def add_action_buttons_kategori(self, row, id_kategori):
        """Add action buttons for kategori"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 0, 5, 0)
        
        user = SessionManager.get_current_user()
        
        if user and user.role == 'admin':
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
            btn_edit.clicked.connect(lambda: self.update_kategori(id_kategori))
            
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
            btn_delete.clicked.connect(lambda: self.delete_kategori(id_kategori))
            
            layout.addWidget(btn_edit)
            layout.addWidget(btn_delete)
        
        layout.addStretch()
        
        self.ui.tableKategori.setCellWidget(row, 2, widget)
    
    def create_item(self, text):
        """Create table item"""
        item = QTableWidgetItem(str(text))
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
        return item
    
    def clear_form_layanan(self):
        """Clear form layanan"""
        self.ui.txtNamaLayanan.clear()
        self.ui.cmbKategori.setCurrentIndex(0)
        self.ui.spinHarga.setValue(0)
        self.ui.timeDurasi.setTime(QTime(1, 0))
        self.ui.txtDeskripsi.clear()
    
    def cancel_form(self, checked=False):
        """Cancel and hide form"""
        self.ui.groupFormLayanan.setVisible(False)
        self.clear_form()
    
    # ============================================
    # Navigation
    # ============================================
    
    def go_dashboard(self):
        from views.main_window import MainWindow
        self.main_window = MainWindow()
        self.main_window.showMaximized()
        self.close()
    
    def go_pelanggan(self):
        from views.pelanggan_view import PelangganView
        self.pelanggan_view = PelangganView()
        self.pelanggan_view.showMaximized()
        self.close()
    
    def go_jadwal(self):
        from views.jadwal_view import JadwalView
        self.jadwal_view = JadwalView()
        self.jadwal_view.showMaximized()
        self.close()
    
    def go_transaksi(self):
        from views.transaksi_view import TransaksiView
        self.transaksi_view = TransaksiView()
        self.transaksi_view.showMaximized()
        self.close()
    
    def go_pembayaran(self):
        from views.pembayaran_view import PembayaranView
        self.pembayaran_view = PembayaranView()
        self.pembayaran_view.showMaximized()
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
            login.showMaximized()
            self.close()