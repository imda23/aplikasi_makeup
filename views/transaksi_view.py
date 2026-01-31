"""
Transaksi View dengan CRUD lengkap
"""
from PyQt5.QtWidgets import (QMainWindow, QMessageBox, QTableWidgetItem, 
                             QPushButton, QHBoxLayout, QWidget, QApplication,
                             QDialog, QVBoxLayout, QLabel, QComboBox, QSpinBox,
                             QDialogButtonBox)
from PyQt5.QtCore import Qt, QDate
from ui.generated.ui_form_transaksi import Ui_MainWindow
from services.transaksi_service import TransaksiService
from services.pelanggan_service import PelangganService
from utils.rbac_decorator import require_role
from utils.rbac_helper import RBACHelper
from services.layanan_service import LayananService
from services.auth_service import AuthService
from utils.session_manager import SessionManager
from utils.formatters import Formatters
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)


class TransaksiView(QMainWindow):
    """View untuk manage transaksi"""
    
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # Services
        self.transaksi_service = TransaksiService()
        self.pelanggan_service = PelangganService()
        self.layanan_service = LayananService()
        
        # State
        self.detail_items = []  # List of {id_layanan, nama_layanan, harga, jumlah, subtotal}
        self.current_transaksi_id = None
        
        # Initialize
        self.init_ui()
        self.connect_signals()
        self.load_pelanggan_combo()
        self.load_jadwal_combo()
        self.load_history()
    
    def init_ui(self):
        """Initialize UI"""
        # Set user info
        user = SessionManager.get_current_user()
        if user:
            self.ui.lblUsername.setText(
                f"👤 {user.nama_user} ({RBACHelper.get_role_name(user.role)})"
            )
            self.setup_rbac_ui(user.role)
            self.setup_menu_visibility(user.role)
        
        # Set tanggal hari ini
        self.ui.dateTanggal.setDate(QDate.currentDate())
        
        # Setup table detail layanan
        self.ui.tableDetailLayanan.setColumnWidth(0, 200)  # Layanan
        self.ui.tableDetailLayanan.setColumnWidth(1, 120)  # Harga
        self.ui.tableDetailLayanan.setColumnWidth(2, 100)  # Jumlah
        self.ui.tableDetailLayanan.setColumnWidth(3, 120)  # Subtotal
        self.ui.tableDetailLayanan.setColumnWidth(4, 100)  # Aksi
        
        # Setup table history
        self.ui.tableHistoryTransaksi.setColumnWidth(0, 100)  # ID
        self.ui.tableHistoryTransaksi.setColumnWidth(1, 120)  # Tanggal
        self.ui.tableHistoryTransaksi.setColumnWidth(2, 150)  # Pelanggan
        self.ui.tableHistoryTransaksi.setColumnWidth(3, 120)  # Total
        self.ui.tableHistoryTransaksi.setColumnWidth(4, 100)  # Status
        self.ui.tableHistoryTransaksi.setColumnWidth(5, 150)  # Aksi
        
        # Reset total
        self.update_total()
    
    def setup_rbac_ui(self, role):
        """Setup UI based on user role"""
        if role == 'owner':
            self.ui.btnTambahLayanan.setVisible(False)
            self.ui.btnSimpanTransaksi.setVisible(False)
            self.ui.groupInfoTransaksi.setEnabled(False)
            self.ui.groupDetailLayanan.setEnabled(False)
    
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
        self.ui.btnJadwal.clicked.connect(self.go_jadwal)
        self.ui.btnTransaksi.clicked.connect(lambda: self.load_history())
        self.ui.btnPembayaran.clicked.connect(self.go_pembayaran)
        self.ui.btnLogout.clicked.connect(self.handle_logout)
        
        # Buttons
        self.ui.btnTambahLayanan.clicked.connect(self.show_dialog_tambah_layanan)
        self.ui.btnSimpanTransaksi.clicked.connect(self.save_transaksi)
        self.ui.btnBatalTransaksi.clicked.connect(self.reset_form)
    
    # ============================================
    # Load Data
    # ============================================
    
    def load_pelanggan_combo(self):
        """Load pelanggan to combobox"""
        try:
            data = self.pelanggan_service.get_all()
            
            self.ui.cmbPelanggan.clear()
            self.ui.cmbPelanggan.addItem("-- Pilih Pelanggan --", None)
            
            for item in data:
                self.ui.cmbPelanggan.addItem(
                    f"{item['nama']} - {item['no_hp']}", 
                    item['id_pelanggan']
                )
            
        except Exception as e:
            logger.error(f"Error loading pelanggan combo: {e}")
    
    def load_jadwal_combo(self):
        """Load jadwal to combobox"""
        try:
            from config.database import Database
            
            # Get jadwal yang statusnya Confirmed atau Completed
            query = """
                SELECT j.id_jadwal, j.tanggal_booking, j.jam_mulai, 
                       p.nama as nama_pelanggan, j.id_pelanggan
                FROM jadwal j
                JOIN pelanggan p ON j.id_pelanggan = p.id_pelanggan
                WHERE j.status IN ('Confirmed', 'Proses', 'Selesai')
                ORDER BY j.tanggal_booking DESC
            """
            data = Database.execute_query(query, fetch=True)
            
            self.ui.cmbJadwal.clear()
            self.ui.cmbJadwal.addItem("-- Pilih Jadwal (Opsional) --", None)
            
            for item in data:
                tanggal = Formatters.format_date(item['tanggal_booking'])
                jam = Formatters.format_time(item['jam_mulai'])
                label = f"{tanggal} {jam} - {item['nama_pelanggan']}"
                
                # Store both id_jadwal and id_pelanggan
                self.ui.cmbJadwal.addItem(label, {
                    'id_jadwal': item['id_jadwal'],
                    'id_pelanggan': item['id_pelanggan']
                })
            
        except Exception as e:
            logger.error(f"Error loading jadwal combo: {e}")
    
    def load_history(self):
        """Load transaction history"""
        try:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            
            data = self.transaksi_service.get_all()
            
            self.ui.tableHistoryTransaksi.setRowCount(0)
            
            for row_idx, item in enumerate(data):
                self.ui.tableHistoryTransaksi.insertRow(row_idx)
                
                # ID Transaksi
                self.ui.tableHistoryTransaksi.setItem(row_idx, 0, 
                    self.create_item(item['id_transaksi']))
                
                # Tanggal
                self.ui.tableHistoryTransaksi.setItem(row_idx, 1, 
                    self.create_item(Formatters.format_date(item['tanggal_transaksi'])))
                
                # Pelanggan
                self.ui.tableHistoryTransaksi.setItem(row_idx, 2, 
                    self.create_item(item['nama_pelanggan']))
                
                # Total
                self.ui.tableHistoryTransaksi.setItem(row_idx, 3, 
                    self.create_item(Formatters.format_currency(item['total'])))
                
                # Status (hardcoded Selesai untuk transaksi yang sudah tersimpan)
                self.ui.tableHistoryTransaksi.setItem(row_idx, 4, 
                    self.create_item("Selesai"))
                
                # Action buttons
                self.add_action_buttons_history(row_idx, item['id_transaksi'])
            
            QApplication.restoreOverrideCursor()
            
        except Exception as e:
            QApplication.restoreOverrideCursor()
            logger.error(f"Error loading history: {e}")
            QMessageBox.critical(self, "Error", "Gagal memuat riwayat transaksi")
    
    # ============================================
    # Detail Layanan Management
    # ============================================
    
    @require_role('admin', 'kasir')
    def show_dialog_tambah_layanan(self, checked=False):
        """Show dialog to add layanan"""
        dialog = TambahLayananDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            layanan_data = dialog.get_data()
            if layanan_data:
                self.add_detail_item(layanan_data)
    
    def add_detail_item(self, layanan_data):
        """Add item to detail layanan table"""
        # Check if layanan already exists
        for item in self.detail_items:
            if item['id_layanan'] == layanan_data['id_layanan']:
                # Update quantity
                item['jumlah'] += layanan_data['jumlah']
                item['subtotal'] = item['harga'] * item['jumlah']
                self.refresh_detail_table()
                self.update_total()
                return
        
        # Add new item
        self.detail_items.append({
            'id_layanan': layanan_data['id_layanan'],
            'nama_layanan': layanan_data['nama_layanan'],
            'harga': layanan_data['harga'],
            'jumlah': layanan_data['jumlah'],
            'subtotal': layanan_data['harga'] * layanan_data['jumlah']
        })
        
        self.refresh_detail_table()
        self.update_total()
    
    def remove_detail_item(self, index):
        """Remove item from detail layanan"""
        reply = QMessageBox.question(
            self, 'Konfirmasi',
            'Hapus layanan ini dari transaksi?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            del self.detail_items[index]
            self.refresh_detail_table()
            self.update_total()
    
    def refresh_detail_table(self):
        """Refresh detail layanan table"""
        self.ui.tableDetailLayanan.setRowCount(0)
        
        for row_idx, item in enumerate(self.detail_items):
            self.ui.tableDetailLayanan.insertRow(row_idx)
            
            # Layanan
            self.ui.tableDetailLayanan.setItem(row_idx, 0, 
                self.create_item(item['nama_layanan']))
            
            # Harga
            self.ui.tableDetailLayanan.setItem(row_idx, 1, 
                self.create_item(Formatters.format_currency(item['harga'])))
            
            # Jumlah
            self.ui.tableDetailLayanan.setItem(row_idx, 2, 
                self.create_item(item['jumlah']))
            
            # Subtotal
            self.ui.tableDetailLayanan.setItem(row_idx, 3, 
                self.create_item(Formatters.format_currency(item['subtotal'])))
            
            # Action button
            self.add_action_button_detail(row_idx, row_idx)
    
    def add_action_button_detail(self, row, index):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 0, 5, 0)
        
        user = SessionManager.get_current_user()
        
        if user and user.role in ['admin', 'kasir']:
            btn_delete = QPushButton("🗑️")
            # ... style ...
            btn_delete.clicked.connect(lambda: self.remove_detail_item(index))
            layout.addWidget(btn_delete)
        
        layout.addStretch()
        self.ui.tableDetailLayanan.setCellWidget(row, 4, widget)
    
    def update_total(self):
        """Update total calculation"""
        subtotal = sum(item['subtotal'] for item in self.detail_items)
        diskon = 0  # TODO: Implement discount logic
        grand_total = subtotal - diskon
        
        self.ui.lblSubtotal.setText(Formatters.format_currency(subtotal))
        self.ui.lblDiskon.setText(Formatters.format_currency(diskon))
        self.ui.lblGrandTotal.setText(Formatters.format_currency(grand_total))
    
    # ============================================
    # Save Transaksi
    # ============================================
    
    @require_role('admin', 'kasir')
    def save_transaksi(self, checked=False):
        """Save transaction"""
        # Validate
        id_pelanggan = self.ui.cmbPelanggan.currentData()
        if id_pelanggan is None:
            QMessageBox.warning(self, "Validasi", "Pelanggan wajib dipilih")
            return
        
        if len(self.detail_items) == 0:
            QMessageBox.warning(self, "Validasi", "Minimal harus ada 1 layanan")
            return
        
        # Get jadwal (optional)
        jadwal_data = self.ui.cmbJadwal.currentData()
        id_jadwal = jadwal_data['id_jadwal'] if jadwal_data else None
        
        # Get tanggal
        tanggal = self.ui.dateTanggal.date().toPyDate()
        
        # Calculate total
        total = sum(item['subtotal'] for item in self.detail_items)
        
        # Get current user
        user = SessionManager.get_current_user()
        id_user = user.id_user if user else None
        
        try:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            
            from config.database import Database
            
            # Insert transaksi
            query = """
                INSERT INTO transaksi (tanggal_transaksi, total, id_user, id_pelanggan, id_jadwal)
                VALUES (%s, %s, %s, %s, %s)
            """
            id_transaksi = Database.execute_query(
                query, 
                (tanggal, total, id_user, id_pelanggan, id_jadwal)
            )
            
            # Insert detail transaksi
            for item in self.detail_items:
                query = """
                    INSERT INTO detail_transaksi (id_transaksi, id_layanan, jumlah, subtotal)
                    VALUES (%s, %s, %s, %s)
                """
                Database.execute_query(
                    query,
                    (id_transaksi, item['id_layanan'], item['jumlah'], item['subtotal'])
                )
            
            QApplication.restoreOverrideCursor()
            
            QMessageBox.information(
                self, 
                "Sukses", 
                f"Transaksi berhasil disimpan!\n\nID Transaksi: {id_transaksi}\nTotal: {Formatters.format_currency(total)}"
            )
            
            # Reset form and reload
            self.reset_form()
            self.load_history()
            
        except Exception as e:
            QApplication.restoreOverrideCursor()
            logger.error(f"Error saving transaksi: {e}")
            QMessageBox.critical(self, "Error", f"Gagal menyimpan transaksi: {str(e)}")
    
    def reset_form(self, checked=False):
        """Reset form"""
        self.ui.cmbPelanggan.setCurrentIndex(0)
        self.ui.cmbJadwal.setCurrentIndex(0)
        self.ui.dateTanggal.setDate(QDate.currentDate())
        self.detail_items.clear()
        self.refresh_detail_table()
        self.update_total()
    
    # ============================================
    # View Detail Transaksi
    # ============================================
    
    def view_detail_transaksi(self, id_transaksi):
        """View transaction detail"""
        try:
            from config.database import Database
            
            # Get transaction data
            query = """
                SELECT t.*, p.nama as nama_pelanggan
                FROM transaksi t
                JOIN pelanggan p ON t.id_pelanggan = p.id_pelanggan
                WHERE t.id_transaksi = %s
            """
            transaksi = Database.execute_query(query, (id_transaksi,), fetch=True)
            
            if not transaksi:
                QMessageBox.warning(self, "Error", "Data tidak ditemukan")
                return
            
            transaksi = transaksi[0]
            
            # Get detail items
            query = """
                SELECT dt.*, l.nama_layanan
                FROM detail_transaksi dt
                JOIN layanan l ON dt.id_layanan = l.id_layanan
                WHERE dt.id_transaksi = %s
            """
            details = Database.execute_query(query, (id_transaksi,), fetch=True)
            
            # Show detail dialog
            detail_text = f"""
DETAIL TRANSAKSI #{id_transaksi}
{'='*50}

Tanggal: {Formatters.format_date(transaksi['tanggal_transaksi'])}
Pelanggan: {transaksi['nama_pelanggan']}

LAYANAN:
{'-'*50}
"""
            for item in details:
                detail_text += f"""
• {item['nama_layanan']}
  Qty: {item['jumlah']} x {Formatters.format_currency(item['subtotal']/item['jumlah'])}
  Subtotal: {Formatters.format_currency(item['subtotal'])}
"""
            
            detail_text += f"""
{'-'*50}
TOTAL: {Formatters.format_currency(transaksi['total'])}
"""
            
            QMessageBox.information(self, "Detail Transaksi", detail_text)
            
        except Exception as e:
            logger.error(f"Error viewing detail: {e}")
            QMessageBox.critical(self, "Error", "Gagal memuat detail transaksi")
    
    # ============================================
    # Helper Methods
    # ============================================
    
    def add_action_buttons_history(self, row, id_transaksi):
        """Add action buttons to history table"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 0, 5, 0)
        
        btn_view = QPushButton("👁️ Lihat")
        btn_view.setStyleSheet("""
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
        btn_view.clicked.connect(lambda: self.view_detail_transaksi(id_transaksi))
        
        layout.addWidget(btn_view)
        layout.addStretch()
        
        self.ui.tableHistoryTransaksi.setCellWidget(row, 5, widget)
    
    def create_item(self, text):
        """Create table item"""
        item = QTableWidgetItem(str(text))
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
        return item
    
    # ============================================
    # Navigation
    # ============================================
    
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


# ============================================
# Dialog Tambah Layanan
# ============================================

class TambahLayananDialog(QDialog):
    """Dialog untuk memilih layanan dan quantity"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layanan_service = LayananService()
        self.init_ui()
    
    def init_ui(self):
        """Initialize dialog UI"""
        self.setWindowTitle("Tambah Layanan")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        # Layanan label
        layout.addWidget(QLabel("Pilih Layanan:"))
        
        # Layanan combobox
        self.cmbLayanan = QComboBox()
        self.load_layanan()
        layout.addWidget(self.cmbLayanan)
        
        # Jumlah label
        layout.addWidget(QLabel("Jumlah:"))
        
        # Jumlah spinbox
        self.spinJumlah = QSpinBox()
        self.spinJumlah.setMinimum(1)
        self.spinJumlah.setMaximum(100)
        self.spinJumlah.setValue(1)
        layout.addWidget(self.spinJumlah)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def load_layanan(self):
        """Load layanan to combobox"""
        try:
            data = self.layanan_service.get_all()
            
            for item in data:
                label = f"{item['nama_layanan']} - {Formatters.format_currency(item['harga'])}"
                self.cmbLayanan.addItem(label, {
                    'id_layanan': item['id_layanan'],
                    'nama_layanan': item['nama_layanan'],
                    'harga': float(item['harga'])
                })
            
        except Exception as e:
            logger.error(f"Error loading layanan: {e}")
    
    def get_data(self):
        """Get selected data"""
        layanan_data = self.cmbLayanan.currentData()
        if layanan_data:
            return {
                'id_layanan': layanan_data['id_layanan'],
                'nama_layanan': layanan_data['nama_layanan'],
                'harga': layanan_data['harga'],
                'jumlah': self.spinJumlah.value()
            }
        return None