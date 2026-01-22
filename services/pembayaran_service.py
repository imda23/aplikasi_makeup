"""Pembayaran service"""
from config.database import Database
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class PembayaranService:
    def get_all(self) -> List[Dict]:
        try:
            query = """
                SELECT pb.*, t.total, p.nama as nama_pelanggan
                FROM pembayaran pb
                JOIN transaksi t ON pb.id_transaksi = t.id_transaksi
                JOIN pelanggan p ON t.id_pelanggan = p.id_pelanggan
                ORDER BY pb.tanggal_bayar DESC
            """
            return Database.execute_query(query, fetch=True)
        except Exception as e:
            logger.error(f"Error get_all: {e}")
            return []