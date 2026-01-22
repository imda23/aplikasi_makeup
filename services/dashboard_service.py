"""Dashboard service"""
from config.database import Database
from datetime import date
import logging

logger = logging.getLogger(__name__)

class DashboardService:
    def get_statistics(self):
        try:
            stats = {}
            
            # Total pelanggan
            query = "SELECT COUNT(*) as total FROM pelanggan"
            result = Database.execute_query(query, fetch=True)
            stats['total_pelanggan'] = result[0]['total']
            
            # Transaksi bulan ini
            query = """
                SELECT COUNT(*) as total FROM transaksi 
                WHERE MONTH(tanggal_transaksi) = MONTH(CURDATE())
                AND YEAR(tanggal_transaksi) = YEAR(CURDATE())
            """
            result = Database.execute_query(query, fetch=True)
            stats['transaksi_bulan_ini'] = result[0]['total']
            
            # Pendapatan hari ini
            query = """
                SELECT COALESCE(SUM(total), 0) as pendapatan FROM transaksi 
                WHERE DATE(tanggal_transaksi) = CURDATE()
            """
            result = Database.execute_query(query, fetch=True)
            stats['pendapatan_hari_ini'] = result[0]['pendapatan']
            
            # Jadwal hari ini
            query = """
                SELECT COUNT(*) as total FROM jadwal 
                WHERE DATE(tanggal_booking) = CURDATE()
            """
            result = Database.execute_query(query, fetch=True)
            stats['jadwal_hari_ini'] = result[0]['total']
            
            return stats
        except Exception as e:
            logger.error(f"Error get_statistics: {e}")
            return {
                'total_pelanggan': 0,
                'transaksi_bulan_ini': 0,
                'pendapatan_hari_ini': 0,
                'jadwal_hari_ini': 0
            }
    
    def get_jadwal_hari_ini(self):
        try:
            query = """
                SELECT j.*, p.nama as nama_pelanggan
                FROM jadwal j
                JOIN pelanggan p ON j.id_pelanggan = p.id_pelanggan
                WHERE DATE(j.tanggal_booking) = CURDATE()
                ORDER BY j.jam_mulai ASC
            """
            return Database.execute_query(query, fetch=True)
        except Exception as e:
            logger.error(f"Error get_jadwal_hari_ini: {e}")
            return []