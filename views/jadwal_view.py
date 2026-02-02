"""
Jadwal View dengan CRUD lengkap
"""
from PyQt5.QtWidgets import (QMainWindow, QMessageBox, QTableWidgetItem, 
                             QPushButton, QHBoxLayout, QWidget, QApplication)
from PyQt5.QtCore import Qt, QDate, QTime
from ui.generated.ui_form_jadwal import Ui_MainWindow
from services.jadwal_service import JadwalService
from services.pelanggan_service import PelangganService
from utils.rbac_decorator import require_role
from utils.rbac_helper import RBACHelper
from services.auth_service import AuthService
from utils.validators import Validators
from utils.session_manager import SessionManager
from utils.formatters import Formatters
from config.constants import StatusJadwal
from datetime import date
import logging

logger = logging.getLogger(__name__)


class JadwalView(QMainWindow):
    """View untuk manage jadwal booking"""
    
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # Services
        self.jadwal_service = JadwalService()
        self.pelanggan_service = PelangganService()
        
        # State
        self.current_mode = "create"  # "create" atau "update"
        self.current_id = None
        
        # Initialize
        self.init_ui()
        self.connect_signals()
        self.load_data()
        self.load_pelanggan_combo()
        self.load_mua_combo()
    
    def init_ui(self):
        """Initialize UI"""
        # Hide form initially
        self.ui.groupFormBooking.setVisible(False)
        
        # Set user info
        user = SessionManager.get_current_user()
        if user:
            self.ui.lblUsername.setText(
                f"👤 {user.nama_user} ({RBACHelper.get_role_name(user.role)})"
            )
            self.setup_rbac_ui(user.role)
            self.setup_menu_visibility(user.role)
        
        # Setup calendar
        self.ui.calendarJadwal.setSelectedDate(QDate.currentDate())
        
        # Setup table
        self.ui.tableJadwal.setColumnWidth(0, 50)   # ID
        self.ui.tableJadwal.setColumnWidth(1, 120)  # Tanggal
        self.ui.tableJadwal.setColumnWidth(2, 100)  # Jam Mulai
        self.ui.tableJadwal.setColumnWidth(3, 100)  # Jam Selesai
        self.ui.tableJadwal.setColumnWidth(4, 150)  # Pelanggan
        self.ui.tableJadwal.setColumnWidth(5, 120)  # MUA
        self.ui.tableJadwal.setColumnWidth(6, 100)  # Status
        self.ui.tableJadwal.setColumnWidth(7, 180)  # Aksi
        
        # Setup status combobox
        self.ui.cmbFilterStatus.clear()
        self.ui.cmbFilterStatus.addItem("Semua Status", None)
        for status in StatusJadwal.get_all():
            self.ui.cmbFilterStatus.addItem(status, status)
        
        # Setup form status combobox
        self.ui.cmbStatus.clear()
        for status in StatusJadwal.get_all():
            self.ui.cmbStatus.addItem(status)
        
        # Set default dates
        self.ui.dateTanggal.setDate(QDate.currentDate())
        self.ui.dateTanggal.setMinimumDate(QDate.currentDate())
        
        # Set default times
        self.ui.timeJamMulai.setTime(QTime(9, 0))
        self.ui.timeJamSelesai.setTime(QTime(10, 30))
    
    def setup_rbac_ui(self, role):
        """Setup UI based on user role"""
        if role == 'owner':
            self.ui.btnBuatJadwal.setVisible(False)
            self.ui.groupFormBooking.setVisible(False)
    
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
        self.ui.btnLayanan.clicked.connect(self.go_layanan)
        self.ui.btnJadwal.clicked.connect(lambda: self.load_data())
        self.ui.btnTransaksi.clicked.connect(self.go_transaksi)
        self.ui.btnPembayaran.clicked.connect(self.go_pembayaran)
        self.ui.btnLogout.clicked.connect(self.handle_logout)
        
        # Filter
        self.ui.cmbFilterStatus.currentIndexChanged.connect(self.filter_by_status)
        
        # Calendar
        self.ui.calendarJadwal.selectionChanged.connect(self.on_date_selected)
        
        # Buttons
        self.ui.btnBuatJadwal.clicked.connect(self.show_form_create)
        self.ui.btnSimpanJadwal.clicked.connect(self.save_jadwal)
        self.ui.btnBatalJadwal.clicked.connect(self.cancel_form)
    
    # ============================================
    # CRUD Operations
    # ============================================
    
    def load_data(self):
        """Load all jadwal"""
        try:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            
            data = self.jadwal_service.get_all()
            
            self.ui.tableJadwal.setRowCount(0)
            
            for row_idx, item in enumerate(data):
                self.ui.tableJadwal.insertRow(row_idx)
                
                # ID
                self.ui.tableJadwal.setItem(row_idx, 0, self.create_item(item['id_jadwal']))
                
                # Tanggal
                self.ui.tableJadwal.setItem(row_idx, 1, self.create_item(Formatters.format_date(item['tanggal_booking'])))
                
                # Jam Mulai
                self.ui.tableJadwal.setItem(row_idx, 2, self.create_item(Formatters.format_time(item['jam_mulai'])))
                
                # Jam Selesai
                self.ui.tableJadwal.setItem(row_idx, 3, self.create_item(Formatters.format_time(item['jam_selesai'])))
                
                # Pelanggan
                self.ui.tableJadwal.setItem(row_idx, 4, self.create_item(item['nama_pelanggan']))
                
                # MUA
                self.ui.tableJadwal.setItem(row_idx, 5, self.create_item(item['nama_mua']))
                
                # Status
                self.ui.tableJadwal.setItem(row_idx, 6, self.create_item(item['status']))
                
                # Action buttons
                self.add_action_buttons(row_idx, item['id_jadwal'])
            
            QApplication.restoreOverrideCursor()
            
        except Exception as e:
            QApplication.restoreOverrideCursor()
            logger.error(f"Error loading data: {e}")
            QMessageBox.critical(self, "Error", "Gagal memuat data")
    
    def filter_by_status(self):
        """Filter jadwal by status"""
        status = self.ui.cmbFilterStatus.currentData()
        
        if status is None:
            # Show all
            for row in range(self.ui.tableJadwal.rowCount()):
                self.ui.tableJadwal.setRowHidden(row, False)
        else:
            # Filter by status
            for row in range(self.ui.tableJadwal.rowCount()):
                item = self.ui.tableJadwal.item(row, 6)  # Status column
                if item:
                    show_row = item.text() == status
                    self.ui.tableJadwal.setRowHidden(row, not show_row)
    
    def on_date_selected(self):
        """When date is selected in calendar"""
        selected_date = self.ui.calendarJadwal.selectedDate()
        self.ui.dateTanggal.setDate(selected_date)
    
    @require_role('admin', 'makeup_artist')
    def show_form_create(self, checked=False):
        """Show form for create jadwal"""
        self.current_mode = "create"
        self.current_id = None
        self.clear_form()
        self.ui.groupFormBooking.setVisible(True)
        self.ui.groupFormBooking.setTitle("📝 Form Booking Baru")
        self.ui.cmbPelanggan.setFocus()
    
    @require_role('admin', 'makeup_artist')
    def show_form_update(self, id_jadwal):
        """Show form for update jadwal"""
        try:
            # Get jadwal data
            data = self.jadwal_service.get_all()
            jadwal = next((item for item in data if item['id_jadwal'] == id_jadwal), None)
            
            if not jadwal:
                QMessageBox.warning(self, "Error", "Data tidak ditemukan")
                return
            
            self.current_mode = "update"
            self.current_id = id_jadwal
            
            # Fill form
            # Set pelanggan
            index = self.ui.cmbPelanggan.findData(jadwal['id_pelanggan'])
            if index >= 0:
                self.ui.cmbPelanggan.setCurrentIndex(index)
            
            # Set MUA
            index = self.ui.cmbMUA.findData(jadwal['id_user'])
            if index >= 0:
                self.ui.cmbMUA.setCurrentIndex(index)
            
            # Set tanggal
            from datetime import datetime
            tanggal = datetime.strptime(str(jadwal['tanggal_booking']), '%Y-%m-%d').date()
            self.ui.dateTanggal.setDate(QDate(tanggal.year, tanggal.month, tanggal.day))
            
            # Set jam mulai
            jam_mulai = datetime.strptime(str(jadwal['jam_mulai']), '%H:%M:%S').time()
            self.ui.timeJamMulai.setTime(QTime(jam_mulai.hour, jam_mulai.minute))
            
            # Set jam selesai
            jam_selesai = datetime.strptime(str(jadwal['jam_selesai']), '%H:%M:%S').time()
            self.ui.timeJamSelesai.setTime(QTime(jam_selesai.hour, jam_selesai.minute))
            
            # Set status
            index = self.ui.cmbStatus.findText(jadwal['status'])
            if index >= 0:
                self.ui.cmbStatus.setCurrentIndex(index)
            
            self.ui.groupFormBooking.setVisible(True)
            self.ui.groupFormBooking.setTitle("📝 Form Edit Booking")
            self.ui.cmbPelanggan.setFocus()
            
        except Exception as e:
            logger.error(f"Error loading for update: {e}")
            QMessageBox.critical(self, "Error", f"Gagal memuat data: {str(e)}")
    
    @require_role('admin', 'makeup_artist')
    def save_jadwal(self, checked=False):
        """Save jadwal"""
        # Get data
        id_pelanggan = self.ui.cmbPelanggan.currentData()
        id_mua = self.ui.cmbMUA.currentData()
        tanggal = self.ui.dateTanggal.date().toPyDate()
        jam_mulai = self.ui.timeJamMulai.time().toString('HH:mm:ss')
        jam_selesai = self.ui.timeJamSelesai.time().toString('HH:mm:ss')
        status = self.ui.cmbStatus.currentText()
        
        # Validate
        if not self.validate_form(id_pelanggan, id_mua, tanggal, 
                                   self.ui.timeJamMulai.time(), 
                                   self.ui.timeJamSelesai.time()):
            return
        
        try:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            
            from config.database import Database
            
            if self.current_mode == "create":
                query = """
                    INSERT INTO jadwal (id_pelanggan, id_user, tanggal_booking, 
                                       jam_mulai, jam_selesai, status) 
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                Database.execute_query(query, (id_pelanggan, id_mua, tanggal, 
                                              jam_mulai, jam_selesai, status))
                message = "Jadwal berhasil dibuat"
            else:
                query = """
                    UPDATE jadwal 
                    SET id_pelanggan=%s, id_user=%s, tanggal_booking=%s, 
                        jam_mulai=%s, jam_selesai=%s, status=%s 
                    WHERE id_jadwal=%s
                """
                Database.execute_query(query, (id_pelanggan, id_mua, tanggal, 
                                              jam_mulai, jam_selesai, status, 
                                              self.current_id))
                message = "Jadwal berhasil diupdate"
            
            QApplication.restoreOverrideCursor()
            
            QMessageBox.information(self, "Sukses", message)
            self.load_data()
            self.cancel_form()
            
        except Exception as e:
            QApplication.restoreOverrideCursor()
            logger.error(f"Error saving: {e}")
            QMessageBox.critical(self, "Error", "Terjadi kesalahan sistem")
    
    @require_role('admin', 'makeup_artist')
    def delete_jadwal(self, id_jadwal):
        """Delete jadwal"""
        reply = QMessageBox.question(
            self, 'Konfirmasi Hapus',
            'Apakah Anda yakin ingin menghapus jadwal ini?\n\n'
            'Data yang sudah dihapus tidak dapat dikembalikan.',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.No:
            return
        
        try:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            
            from config.database import Database
            
            # Check if used in transaksi
            check = "SELECT COUNT(*) as count FROM transaksi WHERE id_jadwal = %s"
            result = Database.execute_query(check, (id_jadwal,), fetch=True)
            if result[0]['count'] > 0:
                QApplication.restoreOverrideCursor()
                QMessageBox.warning(self, "Gagal", "Jadwal sudah digunakan dalam transaksi, tidak dapat dihapus")
                return
            
            query = "DELETE FROM jadwal WHERE id_jadwal = %s"
            Database.execute_query(query, (id_jadwal,))
            
            QApplication.restoreOverrideCursor()
            
            QMessageBox.information(self, "Sukses", "Jadwal berhasil dihapus")
            self.load_data()
            
        except Exception as e:
            QApplication.restoreOverrideCursor()
            logger.error(f"Error deleting: {e}")
            QMessageBox.critical(self, "Error", "Terjadi kesalahan sistem")
    
    # ============================================
    # Helper Methods
    # ============================================
    
    def load_pelanggan_combo(self):
        """Load pelanggan to combobox"""
        try:
            data = self.pelanggan_service.get_all()
            
            self.ui.cmbPelanggan.clear()
            
            for item in data:
                self.ui.cmbPelanggan.addItem(
                    f"{item['nama']} - {item['no_hp']}", 
                    item['id_pelanggan']
                )
            
        except Exception as e:
            logger.error(f"Error loading pelanggan combo: {e}")
    
    def load_mua_combo(self):
        """Load MUA (makeup artist) to combobox"""
        try:
            from config.database import Database
            
            query = """
                SELECT id_user, nama_user 
                FROM user 
                WHERE role = 'makeup_artist'
                ORDER BY nama_user ASC
            """
            data = Database.execute_query(query, fetch=True)
            
            self.ui.cmbMUA.clear()
            
            for item in data:
                self.ui.cmbMUA.addItem(item['nama_user'], item['id_user'])
            
        except Exception as e:
            logger.error(f"Error loading MUA combo: {e}")
    
    def validate_form(self, id_pelanggan, id_mua, tanggal, jam_mulai, jam_selesai):
        """Validate form"""
        # Pelanggan
        if id_pelanggan is None:
            QMessageBox.warning(self, "Validasi", "Pelanggan wajib dipilih")
            self.ui.cmbPelanggan.setFocus()
            return False
        
        # MUA
        if id_mua is None:
            QMessageBox.warning(self, "Validasi", "MUA wajib dipilih")
            self.ui.cmbMUA.setFocus()
            return False
        
        # Tanggal
        is_valid, error = Validators.validate_date_not_past(tanggal)
        if not is_valid:
            QMessageBox.warning(self, "Validasi", error)
            self.ui.dateTanggal.setFocus()
            return False
        
        # Jam
        is_valid, error = Validators.validate_time_range(
            jam_mulai.toPyTime(), 
            jam_selesai.toPyTime()
        )
        if not is_valid:
            QMessageBox.warning(self, "Validasi", error)
            self.ui.timeJamMulai.setFocus()
            return False
        
        return True
    
    def add_action_buttons(self, row, id_jadwal):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 0, 5, 0)
        
        user = SessionManager.get_current_user()
        
        if user and user.role in ['admin', 'makeup_artist']:
            btn_edit = QPushButton("✏️ Edit")
            # ... style ...
            btn_edit.clicked.connect(lambda: self.show_form_update(id_jadwal))
            layout.addWidget(btn_edit)
        
        if user and user.role == 'admin':
            btn_delete = QPushButton("🗑️ Hapus")
            # ... style ...
            btn_delete.clicked.connect(lambda: self.delete_jadwal(id_jadwal))
            layout.addWidget(btn_delete)
        
        layout.addStretch()
        self.ui.tableJadwal.setCellWidget(row, 7, widget)
    
    def create_item(self, text):
        """Create table item"""
        item = QTableWidgetItem(str(text))
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
        return item
    
    def clear_form(self):
        """Clear form"""
        self.ui.cmbPelanggan.setCurrentIndex(0)
        self.ui.cmbMUA.setCurrentIndex(0)
        self.ui.dateTanggal.setDate(QDate.currentDate())
        self.ui.timeJamMulai.setTime(QTime(9, 0))
        self.ui.timeJamSelesai.setTime(QTime(10, 30))
        self.ui.cmbStatus.setCurrentIndex(0)
    
    def cancel_form(self, checked=False):
        """Cancel and hide form"""
        self.ui.groupFormBooking.setVisible(False)
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
    
    def go_layanan(self):
        from views.layanan_view import LayananView
        self.layanan_view = LayananView()
        self.layanan_view.showMaximized()
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