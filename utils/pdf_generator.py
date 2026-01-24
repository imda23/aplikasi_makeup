"""
PDF Generator untuk struk pembayaran
"""
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from datetime import datetime
from utils.formatters import Formatters
from config.settings import Settings
import logging

logger = logging.getLogger(__name__)


class PDFGenerator:
    """Generator untuk membuat PDF struk pembayaran"""
    
    @staticmethod
    def generate_struk_pembayaran(transaksi_data, detail_items, pembayaran_data, filename=None):
        """
        Generate struk pembayaran dalam format PDF
        
        Args:
            transaksi_data: Dict dengan data transaksi
            detail_items: List of dict dengan detail layanan
            pembayaran_data: Dict dengan data pembayaran
            filename: Nama file output (optional)
            
        Returns:
            str: Path ke file PDF yang dibuat
        """
        try:
            # Generate filename jika tidak ada
            if not filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                id_transaksi = transaksi_data['id_transaksi']
                filename = f"struk_{id_transaksi}_{timestamp}.pdf"
            
            # Full path
            filepath = Settings.REPORTS_PDF_DIR / filename
            
            # Ensure directory exists
            Settings.REPORTS_PDF_DIR.mkdir(parents=True, exist_ok=True)
            
            # Create PDF
            c = canvas.Canvas(str(filepath), pagesize=A4)
            width, height = A4
            
            # Starting position
            y = height - 40
            
            # Header - Company Name
            c.setFont("Helvetica-Bold", 20)
            c.drawCentredString(width/2, y, "💄 MAKEUP APP")
            y -= 25
            
            c.setFont("Helvetica", 12)
            c.drawCentredString(width/2, y, "Struk Pembayaran")
            y -= 30
            
            # Garis pemisah
            c.line(50, y, width-50, y)
            y -= 20
            
            # Info Transaksi
            c.setFont("Helvetica-Bold", 10)
            c.drawString(50, y, "INFORMASI TRANSAKSI")
            y -= 15
            
            c.setFont("Helvetica", 10)
            
            # ID Transaksi
            c.drawString(50, y, f"ID Transaksi:")
            c.drawRightString(width-50, y, str(transaksi_data['id_transaksi']))
            y -= 15
            
            # Tanggal Transaksi
            c.drawString(50, y, f"Tanggal Transaksi:")
            c.drawRightString(width-50, y, Formatters.format_date(transaksi_data['tanggal_transaksi']))
            y -= 15
            
            # Pelanggan
            c.drawString(50, y, f"Pelanggan:")
            c.drawRightString(width-50, y, transaksi_data['nama_pelanggan'])
            y -= 15
            
            # ID Pembayaran
            if pembayaran_data.get('id_pembayaran'):
                c.drawString(50, y, f"ID Pembayaran:")
                c.drawRightString(width-50, y, str(pembayaran_data['id_pembayaran']))
                y -= 15
            
            y -= 10
            
            # Garis pemisah
            c.line(50, y, width-50, y)
            y -= 20
            
            # Detail Layanan
            c.setFont("Helvetica-Bold", 10)
            c.drawString(50, y, "DETAIL LAYANAN")
            y -= 20
            
            # Table header
            c.setFont("Helvetica-Bold", 9)
            c.drawString(50, y, "Layanan")
            c.drawString(350, y, "Qty")
            c.drawString(400, y, "Harga")
            c.drawRightString(width-50, y, "Subtotal")
            y -= 15
            
            # Table separator
            c.line(50, y, width-50, y)
            y -= 5
            
            # Detail items
            c.setFont("Helvetica", 9)
            for item in detail_items:
                if y < 100:  # New page if needed
                    c.showPage()
                    y = height - 40
                    c.setFont("Helvetica", 9)
                
                # Layanan name (truncate if too long)
                layanan_name = item['nama_layanan']
                if len(layanan_name) > 40:
                    layanan_name = layanan_name[:37] + "..."
                
                c.drawString(50, y, layanan_name)
                c.drawString(350, y, str(item['jumlah']))
                c.drawString(400, y, Formatters.format_currency(item['harga']))
                c.drawRightString(width-50, y, Formatters.format_currency(item['subtotal']))
                y -= 15
            
            y -= 5
            
            # Garis pemisah
            c.line(50, y, width-50, y)
            y -= 20
            
            # Total section
            c.setFont("Helvetica-Bold", 11)
            
            # Total Tagihan
            c.drawString(350, y, "Total Tagihan:")
            c.drawRightString(width-50, y, Formatters.format_currency(transaksi_data['total']))
            y -= 20
            
            # Jumlah Bayar
            c.drawString(350, y, "Jumlah Bayar:")
            c.drawRightString(width-50, y, Formatters.format_currency(pembayaran_data['jumlah_bayar']))
            y -= 20
            
            # Kembalian
            kembalian = pembayaran_data['jumlah_bayar'] - float(transaksi_data['total'])
            c.drawString(350, y, "Kembalian:")
            c.drawRightString(width-50, y, Formatters.format_currency(kembalian if kembalian >= 0 else 0))
            y -= 25
            
            # Garis tebal
            c.setLineWidth(2)
            c.line(50, y, width-50, y)
            c.setLineWidth(1)
            y -= 20
            
            # Payment info
            c.setFont("Helvetica", 10)
            c.drawString(50, y, f"Metode Pembayaran:")
            c.drawRightString(width-50, y, pembayaran_data['metode_bayar'])
            y -= 15
            
            c.drawString(50, y, f"Status Pembayaran:")
            c.drawRightString(width-50, y, pembayaran_data['status'])
            y -= 15
            
            c.drawString(50, y, f"Tanggal Pembayaran:")
            c.drawRightString(width-50, y, Formatters.format_date(pembayaran_data['tanggal_bayar']))
            y -= 30
            
            # Footer
            c.line(50, y, width-50, y)
            y -= 20
            
            c.setFont("Helvetica-Bold", 11)
            c.drawCentredString(width/2, y, "Terima Kasih")
            y -= 15
            
            c.setFont("Helvetica", 10)
            c.drawCentredString(width/2, y, "Selamat Datang Kembali")
            y -= 20
            
            # Print date
            c.setFont("Helvetica", 8)
            print_time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            c.drawCentredString(width/2, y, f"Dicetak: {print_time}")
            
            # Save PDF
            c.save()
            
            logger.info(f"✅ PDF struk berhasil dibuat: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"❌ Error generating PDF: {e}")
            raise
    
    @staticmethod
    def generate_struk_thermal(transaksi_data, detail_items, pembayaran_data, filename=None):
        """
        Generate struk format thermal printer (58mm atau 80mm)
        Untuk printer kasir
        
        Args:
            transaksi_data: Dict dengan data transaksi
            detail_items: List of dict dengan detail layanan
            pembayaran_data: Dict dengan data pembayaran
            filename: Nama file output (optional)
            
        Returns:
            str: Path ke file PDF yang dibuat
        """
        try:
            # Generate filename
            if not filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                id_transaksi = transaksi_data['id_transaksi']
                filename = f"struk_thermal_{id_transaksi}_{timestamp}.pdf"
            
            # Full path
            filepath = Settings.REPORTS_PDF_DIR / filename
            
            # Thermal printer paper size (80mm width)
            page_width = 80 * mm
            page_height = 297 * mm  # A4 height, will be auto-adjusted
            
            # Create PDF
            c = canvas.Canvas(str(filepath), pagesize=(page_width, page_height))
            
            # Starting position
            y = page_height - 10
            margin = 5
            
            # Header
            c.setFont("Helvetica-Bold", 12)
            c.drawCentredString(page_width/2, y, "MAKEUP APP")
            y -= 12
            
            c.setFont("Helvetica", 8)
            c.drawCentredString(page_width/2, y, "Struk Pembayaran")
            y -= 10
            
            c.line(margin, y, page_width-margin, y)
            y -= 10
            
            # Info Transaksi
            c.setFont("Helvetica", 7)
            c.drawString(margin, y, f"ID Trans : {transaksi_data['id_transaksi']}")
            y -= 8
            c.drawString(margin, y, f"Tanggal  : {Formatters.format_date(transaksi_data['tanggal_transaksi'])}")
            y -= 8
            c.drawString(margin, y, f"Pelanggan: {transaksi_data['nama_pelanggan']}")
            y -= 10
            
            c.line(margin, y, page_width-margin, y)
            y -= 10
            
            # Detail Layanan
            for item in detail_items:
                # Layanan name
                layanan = item['nama_layanan']
                if len(layanan) > 25:
                    layanan = layanan[:22] + "..."
                
                c.drawString(margin, y, layanan)
                y -= 8
                
                # Qty x Harga = Subtotal
                detail_line = f"{item['jumlah']}x {Formatters.format_currency(item['harga'])}"
                c.drawString(margin + 5, y, detail_line)
                c.drawRightString(page_width-margin, y, Formatters.format_currency(item['subtotal']))
                y -= 10
            
            c.line(margin, y, page_width-margin, y)
            y -= 10
            
            # Totals
            c.setFont("Helvetica-Bold", 8)
            c.drawString(margin, y, "Total:")
            c.drawRightString(page_width-margin, y, Formatters.format_currency(transaksi_data['total']))
            y -= 10
            
            c.drawString(margin, y, "Bayar:")
            c.drawRightString(page_width-margin, y, Formatters.format_currency(pembayaran_data['jumlah_bayar']))
            y -= 10
            
            kembalian = pembayaran_data['jumlah_bayar'] - float(transaksi_data['total'])
            c.drawString(margin, y, "Kembali:")
            c.drawRightString(page_width-margin, y, Formatters.format_currency(kembalian if kembalian >= 0 else 0))
            y -= 12
            
            c.line(margin, y, page_width-margin, y)
            y -= 10
            
            # Payment info
            c.setFont("Helvetica", 7)
            c.drawString(margin, y, f"Metode: {pembayaran_data['metode_bayar']}")
            y -= 8
            c.drawString(margin, y, f"Status: {pembayaran_data['status']}")
            y -= 12
            
            # Footer
            c.drawCentredString(page_width/2, y, "Terima Kasih")
            y -= 8
            c.drawCentredString(page_width/2, y, "Selamat Datang Kembali")
            y -= 10
            
            print_time = datetime.now().strftime('%d/%m/%Y %H:%M')
            c.setFont("Helvetica", 6)
            c.drawCentredString(page_width/2, y, f"Print: {print_time}")
            
            # Save
            c.save()
            
            logger.info(f"✅ PDF thermal struk berhasil dibuat: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"❌ Error generating thermal PDF: {e}")
            raise