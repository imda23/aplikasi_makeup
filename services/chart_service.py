"""
Chart service untuk statistik
"""
from config.database import Database
import logging

logger = logging.getLogger(__name__)


class ChartService:
    """Service untuk data chart/statistik"""
    
    @staticmethod
    def get_transaksi_per_bulan(tahun=None):
        """
        Get transaksi per bulan untuk chart
        
        Args:
            tahun: Tahun yang dipilih (default tahun ini)
            
        Returns:
            dict: {bulan: total_transaksi}
        """
        try:
            if tahun is None:
                tahun = "YEAR(CURDATE())"
            else:
                tahun = f"'{tahun}'"
            
            query = f"""
                SELECT 
                    MONTH(tanggal_transaksi) as bulan,
                    COUNT(*) as total
                FROM transaksi
                WHERE YEAR(tanggal_transaksi) = {tahun}
                GROUP BY MONTH(tanggal_transaksi)
                ORDER BY bulan
            """
            
            result = Database.execute_query(query, fetch=True)
            
            # Initialize all months with 0
            data = {i: 0 for i in range(1, 13)}
            
            # Fill with actual data
            for row in result:
                data[row['bulan']] = row['total']
            
            return data
            
        except Exception as e:
            logger.error(f"Error get_transaksi_per_bulan: {e}")
            return {i: 0 for i in range(1, 13)}
    
    @staticmethod
    def get_pendapatan_per_bulan(tahun=None):
        """
        Get pendapatan per bulan untuk chart
        
        Args:
            tahun: Tahun yang dipilih (default tahun ini)
            
        Returns:
            dict: {bulan: total_pendapatan}
        """
        try:
            if tahun is None:
                tahun = "YEAR(CURDATE())"
            else:
                tahun = f"'{tahun}'"
            
            query = f"""
                SELECT 
                    MONTH(tanggal_transaksi) as bulan,
                    COALESCE(SUM(total), 0) as total_pendapatan
                FROM transaksi
                WHERE YEAR(tanggal_transaksi) = {tahun}
                GROUP BY MONTH(tanggal_transaksi)
                ORDER BY bulan
            """
            
            result = Database.execute_query(query, fetch=True)
            
            # Initialize all months with 0
            data = {i: 0.0 for i in range(1, 13)}
            
            # Fill with actual data
            for row in result:
                pendapatan = row['total_pendapatan']
                if pendapatan is not None and pendapatan != 0:
                    data[row['bulan']] = float(pendapatan)
                else:
                    data[row['bulan']] = 0.0
            
            return data
            
        except Exception as e:
            logger.error(f"Error get_pendapatan_per_bulan: {e}")
            return {i: 0.0 for i in range(1, 13)}
    
    @staticmethod
    def get_tahun_tersedia():
        """
        Get list tahun yang tersedia di database
        
        Returns:
            list: [2024, 2025, ...]
        """
        try:
            query = """
                SELECT DISTINCT YEAR(tanggal_transaksi) as tahun
                FROM transaksi
                ORDER BY tahun DESC
            """
            
            result = Database.execute_query(query, fetch=True)
            
            return [row['tahun'] for row in result]
            
        except Exception as e:
            logger.error(f"Error get_tahun_tersedia: {e}")
            return []