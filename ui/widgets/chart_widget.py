"""
Chart Widget menggunakan matplotlib
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLabel
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from services.chart_service import ChartService
from datetime import datetime
import numpy as np
import logging

logger = logging.getLogger(__name__)


class ChartWidget(QWidget):
    """Widget untuk menampilkan chart statistik"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.chart_service = ChartService()
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        
        # Header dengan filter tahun
        header_layout = QHBoxLayout()
        
        label = QLabel("📊 Statistik Transaksi & Pendapatan")
        label.setStyleSheet("""
            font-size: 14pt;
            font-weight: bold;
            color: #E91E63;
        """)
        header_layout.addWidget(label)
        
        header_layout.addStretch()
        
        # Filter tahun
        self.label_tahun = QLabel("Tahun:")
        self.label_tahun.setStyleSheet("font-weight: bold;")
        header_layout.addWidget(self.label_tahun)
        
        self.cmb_tahun = QComboBox()
        self.cmb_tahun.setStyleSheet("""
            QComboBox {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 5px 10px;
                min-width: 100px;
            }
        """)
        self.cmb_tahun.currentTextChanged.connect(self.update_chart)
        header_layout.addWidget(self.cmb_tahun)
        
        layout.addLayout(header_layout)
        
        # Chart canvas
        self.figure = Figure(figsize=(12, 5))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        self.setLayout(layout)
        
        # Load data
        self.load_tahun()
        self.update_chart()
    
    def load_tahun(self):
        """Load available years"""
        tahun_list = self.chart_service.get_tahun_tersedia()
        
        # Add current year if not in list
        current_year = datetime.now().year
        if current_year not in tahun_list:
            tahun_list.insert(0, current_year)
        
        self.cmb_tahun.clear()
        for tahun in tahun_list:
            self.cmb_tahun.addItem(str(tahun))
    
    def update_chart(self):
        """Update chart dengan data terbaru"""
        try:
            tahun = self.cmb_tahun.currentText()
            
            if not tahun:
                return
            
            # Get data
            transaksi_data = self.chart_service.get_transaksi_per_bulan(int(tahun))
            pendapatan_data = self.chart_service.get_pendapatan_per_bulan(int(tahun))
            
            # Clear figure
            self.figure.clear()
            
            # Create subplots
            ax1 = self.figure.add_subplot(121)
            ax2 = self.figure.add_subplot(122)
            
            # Nama bulan
            bulan_names = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 
                           'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des']
            
            # Data untuk plot - konversi eksplisit
            months = list(range(1, 13))
            transaksi_values = [int(transaksi_data[m]) for m in months]
            pendapatan_values = [float(pendapatan_data[m]) / 1000000.0 for m in months]
            
            # Chart 1: Jumlah Transaksi (Bar Chart)
            ax1.bar(bulan_names, transaksi_values, color='#E91E63', alpha=0.7)
            ax1.set_title(f'Jumlah Transaksi per Bulan ({tahun})', 
                          fontsize=12, fontweight='bold')
            ax1.set_xlabel('Bulan', fontsize=10)
            ax1.set_ylabel('Jumlah Transaksi', fontsize=10)
            ax1.grid(axis='y', alpha=0.3)
            ax1.tick_params(axis='x', rotation=45)
            
            # Tambahkan nilai di atas bar
            for i, v in enumerate(transaksi_values):
                if v > 0:
                    ax1.text(i, v + 0.1, str(int(v)), 
                            ha='center', va='bottom', fontsize=9)
            
            # Chart 2: Pendapatan (Line Chart)
            # Convert to numpy arrays untuk kompatibilitas
            x_values = np.arange(len(bulan_names))
            y_values = np.array(pendapatan_values)
            
            ax2.plot(bulan_names, y_values, 
                    color='#4CAF50', marker='o', linewidth=2, markersize=6)
            ax2.fill_between(x_values, 0, y_values, 
                             alpha=0.3, color='#4CAF50')
            
            ax2.set_title(f'Pendapatan per Bulan ({tahun})', 
                         fontsize=12, fontweight='bold')
            ax2.set_xlabel('Bulan', fontsize=10)
            ax2.set_ylabel('Pendapatan (Juta Rp)', fontsize=10)
            ax2.grid(axis='y', alpha=0.3)
            ax2.tick_params(axis='x', rotation=45)
            
            # Tambahkan nilai di titik
            for i, v in enumerate(pendapatan_values):
                if v > 0:
                    max_val = max(pendapatan_values) if max(pendapatan_values) > 0 else 1.0
                    ax2.text(i, v + (max_val * 0.02), 
                            f'{v:.1f}', 
                            ha='center', va='bottom', fontsize=9)
            
            # Adjust layout
            self.figure.tight_layout()
            
            # Refresh canvas
            self.canvas.draw()
            
        except Exception as e:
            logger.error(f"Error updating chart: {e}")