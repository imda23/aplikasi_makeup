"""
Pembayaran View dengan logika lengkap
"""
from PyQt5.QtWidgets import (QMainWindow, QMessageBox, QTableWidgetItem, 
                             QApplication)
from PyQt5.QtCore import Qt, QDate
from ui.generated.ui_form_pembayaran import Ui_MainWindow
from services.pembayaran_service import PembayaranService
from services.auth_service import AuthService
from utils.session_manager import SessionManager
from utils.formatters import Formatters
from config.constants import StatusPembayaran, MetodePembayaran
import logging

logger = logging.getLogger(__name__)


class PembayaranView(QMainWindow):
    """View untuk manage pembayaran"""
    
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # Services
        self.pembayaran_service = PembayaranService()
        
        # State
        self.current_transaksi = None
        self.current_detail_transaksi = []
        
        # Initialize
        self.init_ui()
        self.connect_signals()
        self.load_history()
    
    def init_ui(self):
        """Initialize UI"""
        # Set user info
        user = SessionManager.get_current_user()
        if user:
            self.ui.lblUsername.setText(f"👤 {user.nama_user}")
        
        # Set tanggal hari ini
        self.ui.dateTanggalBayar.setDate(QDate.currentDate())
        
        # Setup metode pembayaran combobox
        self.ui.cmbMetodePembayaran.clear()
        for metode in MetodePembayaran.get_all():
            self.ui.cmbMetodePembayaran.addItem(metode)
        
        # Setup status pembayaran combobox
        self.ui.cmbStatusPembayaran.clear()
        for status in StatusPembayaran.get_all():
            self.ui.cmbStatusPembayaran.addItem(status)
        
        # Connect spinbox change to calculate kembalian
        self.ui.spinJumlahBayar.valueChanged.connect(self.calculate_kembalian)
        
        # Setup table widths
        self.ui.tableDetailTransaksi.setColumnWidth(0, 200)  # Layanan
        self.ui.tableDetailTransaksi.setColumnWidth(1, 80)   # Qty
        self.ui.tableDetailTransaksi.setColumnWidth(2, 120)  # Harga
        self.ui.tableDetailTransaksi.setColumnWidth(3, 120)  # Subtotal
        
        self.ui.tableHistoryPembayaran.setColumnWidth(0, 100)  # ID Pembayaran
        self.ui.tableHistoryPembayaran.setColumnWidth(1, 100)  # ID Transaksi
        self.ui.tableHistoryPembayaran.setColumnWidth(2, 150)  # Pelanggan
        self.ui.tableHistoryPembayaran.setColumnWidth(3, 120)  # Jumlah
        self.ui.tableHistoryPembayaran.setColumnWidth(4, 150)  # Metode
        self.ui.tableHistoryPembayaran.setColumnWidth(5, 120)  # Tanggal
        self.ui.tableHistoryPembayaran.setColumnWidth(6, 100)  # Status
    
    def connect_signals(self):
        """Connect signals"""
        # Navigation
        self.ui.btnDashboard.clicked.connect(self.go_dashboard)
        self.ui.btnPelanggan.clicked.connect(self.go_pelanggan)
        self.ui.btnLayanan.clicked.connect(self.go_layanan)
        self.ui.btnJadwal.clicked.connect(self.go_jadwal)
        self.ui.btnTransaksi.clicked.connect(self.go_transaksi)
        self.ui.btnPembayaran.clicked.connect(lambda: self.load_history())
        self.ui.btnLogout.clicked.connect(self.handle_logout)
        
        # Buttons
        self.ui.btnCari.clicked.connect(self.search_transaksi)
        self.ui.btnProsesPembayaran.clicked.connect(self.proses_pembayaran)
        self.ui.btnCetakStruk.clicked.connect(self.cetak_struk)
        
        # Enter key untuk search
        self.ui.txtSearchTransaksi.returnPressed.connect(self.search_transaksi)
    
    # ============================================
    # Search & Load Transaksi
    # ============================================
    
    def search_transaksi(self):
        """Search transaksi by ID or customer name"""
        keyword = self.ui.txtSearchTransaksi.text().strip()
        
        if not keyword:
            QMessageBox.warning(self, "Validasi", "Masukkan ID Transaksi atau Nama Pelanggan")
            return
        
        try:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            
            from config.database import Database
            
            # Search by ID or name
            if keyword.isdigit():
                # Search by ID
                query = """
                    SELECT t.*, p.nama as nama_pelanggan
                    FROM transaksi t
                    JOIN pelanggan p ON t.id_pelanggan = p.id_pelanggan
                    WHERE t.id_transaksi = %s
                """
                result = Database.execute_query(query, (int(keyword),), fetch=True)
            else:
                # Search by name
                query = """
                    SELECT t.*, p.nama as nama_pelanggan
                    FROM transaksi t
                    JOIN pelanggan p ON t.id_pelanggan = p.id_pelanggan
                    WHERE p.nama LIKE %s
                    ORDER BY t.tanggal_transaksi DESC
                    LIMIT 1
                """
                result = Database.execute_query(query, (f"%{keyword}%",), fetch=True)
            
            QApplication.restoreOverrideCursor()
            
            if not result:
                QMessageBox.warning(self, "Tidak Ditemukan", "Transaksi tidak ditemukan")
                self.clear_detail()
                return
            
            # Check if already paid
            transaksi = result[0]
            check_query = "SELECT COUNT(*) as count FROM pembayaran WHERE id_transaksi = %s AND status = 'Lunas'"
            check_result = Database.execute_query(check_query, (transaksi['id_transaksi'],), fetch=True)
            
            if check_result[0]['count'] > 0:
                QMessageBox.information(
                    self, 
                    "Sudah Lunas", 
                    f"Transaksi #{transaksi['id_transaksi']} sudah dibayar lunas.\n\nSilakan cari transaksi lain."
                )
                self.clear_detail()
                return
            
            # Load transaksi detail
            self.load_transaksi_detail(transaksi)
            
        except Exception as e:
            QApplication.restoreOverrideCursor()
            logger.error(f"Error searching transaksi: {e}")
            QMessageBox.critical(self, "Error", f"Gagal mencari transaksi: {str(e)}")
    
    def load_transaksi_detail(self, transaksi):
        """Load transaction detail"""
        try:
            from config.database import Database
            
            # Save current transaksi
            self.current_transaksi = transaksi
            
            # Update info labels
            self.ui.lblIDTransaksi.setText(str(transaksi['id_transaksi']))
            self.ui.lblNamaPelanggan.setText(transaksi['nama_pelanggan'])
            self.ui.lblTanggalTransaksi.setText(Formatters.format_date(transaksi['tanggal_transaksi']))
            
            # Get detail items
            query = """
                SELECT dt.*, l.nama_layanan, l.harga
                FROM detail_transaksi dt
                JOIN layanan l ON dt.id_layanan = l.id_layanan
                WHERE dt.id_transaksi = %s
            """
            details = Database.execute_query(query, (transaksi['id_transaksi'],), fetch=True)
            
            self.current_detail_transaksi = details
            
            # Clear and populate table
            self.ui.tableDetailTransaksi.setRowCount(0)
            
            for row_idx, item in enumerate(details):
                self.ui.tableDetailTransaksi.insertRow(row_idx)
                
                # Layanan
                self.ui.tableDetailTransaksi.setItem(row_idx, 0, 
                    self.create_item(item['nama_layanan']))
                
                # Qty
                self.ui.tableDetailTransaksi.setItem(row_idx, 1, 
                    self.create_item(item['jumlah']))
                
                # Harga
                self.ui.tableDetailTransaksi.setItem(row_idx, 2, 
                    self.create_item(Formatters.format_currency(item['harga'])))
                
                # Subtotal
                self.ui.tableDetailTransaksi.setItem(row_idx, 3, 
                    self.create_item(Formatters.format_currency(item['subtotal'])))
            
            # Update total labels
            total = float(transaksi['total'])
            self.ui.lblTotalTagihan.setText(f"Total: {Formatters.format_currency(total)}")
            self.ui.lblTotalTagihan2.setText(Formatters.format_currency(total))
            
            # Set jumlah bayar to total
            self.ui.spinJumlahBayar.setValue(int(total))
            
            # Enable form
            self.ui.widgetPembayaranContent.setEnabled(True)
            
            QMessageBox.information(
                self, 
                "Transaksi Ditemukan", 
                f"Transaksi #{transaksi['id_transaksi']} berhasil dimuat.\n\n"
                f"Total Tagihan: {Formatters.format_currency(total)}"
            )
            
        except Exception as e:
            logger.error(f"Error loading transaksi detail: {e}")
            QMessageBox.critical(self, "Error", "Gagal memuat detail transaksi")
    
    def clear_detail(self):
        """Clear detail form"""
        self.current_transaksi = None
        self.current_detail_transaksi = []
        
        self.ui.lblIDTransaksi.setText("-")
        self.ui.lblNamaPelanggan.setText("-")
        self.ui.lblTanggalTransaksi.setText("-")
        self.ui.lblTotalTagihan.setText("Total: Rp 0")
        self.ui.lblTotalTagihan2.setText("Rp 0")
        self.ui.lblJumlahBayar.setText("Rp 0")
        self.ui.lblKembalian.setText("Rp 0")
        
        self.ui.tableDetailTransaksi.setRowCount(0)
        self.ui.spinJumlahBayar.setValue(0)
        
        self.ui.widgetPembayaranContent.setEnabled(False)
    
    # ============================================
    # Calculate Kembalian
    # ============================================
    
    def calculate_kembalian(self):
        """Calculate change (kembalian)"""
        if not self.current_transaksi:
            return
        
        total_tagihan = float(self.current_transaksi['total'])
        jumlah_bayar = self.ui.spinJumlahBayar.value()
        
        kembalian = jumlah_bayar - total_tagihan
        
        # Update labels
        self.ui.lblJumlahBayar.setText(Formatters.format_currency(jumlah_bayar))
        
        if kembalian >= 0:
            self.ui.lblKembalian.setText(Formatters.format_currency(kembalian))
            self.ui.lblKembalian.setStyleSheet("color: #4CAF50;")
        else:
            self.ui.lblKembalian.setText(Formatters.format_currency(abs(kembalian)))
            self.ui.lblKembalian.setStyleSheet("color: #f44336;")
    
    # ============================================
    # Proses Pembayaran
    # ============================================
    
    def proses_pembayaran(self):
        """Process payment"""
        # Validate
        if not self.current_transaksi:
            QMessageBox.warning(self, "Validasi", "Belum ada transaksi yang dipilih.\n\nSilakan cari transaksi terlebih dahulu.")
            return
        
        jumlah_bayar = self.ui.spinJumlahBayar.value()
        total_tagihan = float(self.current_transaksi['total'])
        
        if jumlah_bayar <= 0:
            QMessageBox.warning(self, "Validasi", "Jumlah bayar harus lebih dari 0")
            return
        
        # For status Belum Lunas or DP, allow partial payment
        status = self.ui.cmbStatusPembayaran.currentText()
        if status == StatusPembayaran.LUNAS and jumlah_bayar < total_tagihan:
            QMessageBox.warning(
                self, 
                "Validasi", 
                f"Jumlah bayar kurang dari total tagihan.\n\n"
                f"Total: {Formatters.format_currency(total_tagihan)}\n"
                f"Bayar: {Formatters.format_currency(jumlah_bayar)}\n\n"
                f"Silakan ubah status menjadi 'Belum Lunas' atau 'DP' untuk pembayaran sebagian."
            )
            return
        
        # Confirmation
        kembalian = jumlah_bayar - total_tagihan
        metode = self.ui.cmbMetodePembayaran.currentText()
        tanggal = self.ui.dateTanggalBayar.date().toPyDate()
        
        confirm_text = f"""
KONFIRMASI PEMBAYARAN

Transaksi ID: {self.current_transaksi['id_transaksi']}
Pelanggan: {self.current_transaksi['nama_pelanggan']}

Total Tagihan: {Formatters.format_currency(total_tagihan)}
Jumlah Bayar: {Formatters.format_currency(jumlah_bayar)}
Kembalian: {Formatters.format_currency(kembalian if kembalian >= 0 else 0)}

Metode: {metode}
Status: {status}
Tanggal: {Formatters.format_date(tanggal)}

Proses pembayaran ini?
"""
        
        reply = QMessageBox.question(
            self, 
            'Konfirmasi Pembayaran',
            confirm_text,
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.No:
            return
        
        # Save pembayaran
        try:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            
            from config.database import Database
            
            query = """
                INSERT INTO pembayaran (id_transaksi, jumlah_bayar, metode_bayar, 
                                       tanggal_bayar, status)
                VALUES (%s, %s, %s, %s, %s)
            """
            id_pembayaran = Database.execute_query(
                query,
                (self.current_transaksi['id_transaksi'], jumlah_bayar, metode, tanggal, status)
            )
            
            QApplication.restoreOverrideCursor()
            
            QMessageBox.information(
                self,
                "Sukses",
                f"✅ Pembayaran berhasil diproses!\n\n"
                f"ID Pembayaran: {id_pembayaran}\n"
                f"Kembalian: {Formatters.format_currency(kembalian if kembalian >= 0 else 0)}\n\n"
                f"Silakan cetak struk pembayaran."
            )
            
            # Reload history and clear form
            self.load_history()
            self.clear_detail()
            self.ui.txtSearchTransaksi.clear()
            
        except Exception as e:
            QApplication.restoreOverrideCursor()
            logger.error(f"Error saving pembayaran: {e}")
            QMessageBox.critical(self, "Error", f"Gagal menyimpan pembayaran: {str(e)}")
    
    # ============================================
    # Cetak Struk
    # ============================================
    
    def cetak_struk(self):
        """Print receipt to PDF"""
        if not self.current_transaksi:
            QMessageBox.warning(self, "Validasi", "Belum ada transaksi yang dipilih")
            return
        
        try:
            from utils.pdf_generator import PDFGenerator
            from PyQt5.QtGui import QDesktopServices
            from PyQt5.QtCore import QUrl
            
            # Prepare data
            pembayaran_data = {
                'id_pembayaran': None,
                'jumlah_bayar': self.ui.spinJumlahBayar.value(),
                'metode_bayar': self.ui.cmbMetodePembayaran.currentText(),
                'tanggal_bayar': self.ui.dateTanggalBayar.date().toPyDate(),
                'status': self.ui.cmbStatusPembayaran.currentText()
            }
            
            # Ask user which format - Simple version without nested imports
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Question)
            msg.setWindowTitle('Format Struk')
            msg.setText('Pilih format struk:')
            msg.setInformativeText('Yes = Format A4 (Standar)\nNo = Format Thermal (Printer Kasir)')
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            msg.setDefaultButton(QMessageBox.Yes)
            
            reply = msg.exec_()
            
            if reply == QMessageBox.Cancel:
                return
            
            QApplication.setOverrideCursor(Qt.WaitCursor)
            
            # Generate PDF
            if reply == QMessageBox.Yes:
                filepath = PDFGenerator.generate_struk_pembayaran(
                    self.current_transaksi,
                    self.current_detail_transaksi,
                    pembayaran_data
                )
            else:
                filepath = PDFGenerator.generate_struk_thermal(
                    self.current_transaksi,
                    self.current_detail_transaksi,
                    pembayaran_data
                )
            
            QApplication.restoreOverrideCursor()
            
            # Ask to open PDF
            msg2 = QMessageBox(self)
            msg2.setIcon(QMessageBox.Information)
            msg2.setWindowTitle('Struk Berhasil Dibuat')
            msg2.setText('✅ Struk pembayaran berhasil dibuat!')
            msg2.setInformativeText(f'Lokasi: {filepath}\n\nBuka file PDF sekarang?')
            msg2.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg2.setDefaultButton(QMessageBox.Yes)
            
            if msg2.exec_() == QMessageBox.Yes:
                QDesktopServices.openUrl(QUrl.fromLocalFile(filepath))
            
        except Exception as e:
            QApplication.restoreOverrideCursor()
            logger.error(f"Error cetak struk: {e}")
            QMessageBox.critical(self, "Error", f"Gagal membuat struk PDF:\n{str(e)}")
    
    # ============================================
    # Load History
    # ============================================
    
    def load_history(self):
        """Load payment history"""
        try:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            
            data = self.pembayaran_service.get_all()
            
            self.ui.tableHistoryPembayaran.setRowCount(0)
            
            for row_idx, item in enumerate(data):
                self.ui.tableHistoryPembayaran.insertRow(row_idx)
                
                # ID Pembayaran
                self.ui.tableHistoryPembayaran.setItem(row_idx, 0, 
                    self.create_item(item['id_pembayaran']))
                
                # ID Transaksi
                self.ui.tableHistoryPembayaran.setItem(row_idx, 1, 
                    self.create_item(item['id_transaksi']))
                
                # Pelanggan
                self.ui.tableHistoryPembayaran.setItem(row_idx, 2, 
                    self.create_item(item['nama_pelanggan']))
                
                # Jumlah
                self.ui.tableHistoryPembayaran.setItem(row_idx, 3, 
                    self.create_item(Formatters.format_currency(item['jumlah_bayar'])))
                
                # Metode
                self.ui.tableHistoryPembayaran.setItem(row_idx, 4, 
                    self.create_item(item['metode_bayar']))
                
                # Tanggal
                self.ui.tableHistoryPembayaran.setItem(row_idx, 5, 
                    self.create_item(Formatters.format_date(item['tanggal_bayar'])))
                
                # Status
                self.ui.tableHistoryPembayaran.setItem(row_idx, 6, 
                    self.create_item(item['status']))
            
            QApplication.restoreOverrideCursor()
            
        except Exception as e:
            QApplication.restoreOverrideCursor()
            logger.error(f"Error loading history: {e}")
            QMessageBox.critical(self, "Error", "Gagal memuat riwayat pembayaran")
    
    # ============================================
    # Helper Methods
    # ============================================
    
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
    
    def go_transaksi(self):
        from views.transaksi_view import TransaksiView
        self.transaksi_view = TransaksiView()
        self.transaksi_view.show()
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