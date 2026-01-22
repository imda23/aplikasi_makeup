"""Transaksi service"""
from config.database import Database
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class TransaksiService:
    def get_all(self) -> List[Dict]:
        try:
            query = """
                SELECT t.*, p.nama as nama_pelanggan
                FROM transaksi t
                JOIN pelanggan p ON t.id_pelanggan = p.id_pelanggan
                ORDER BY t.tanggal_transaksi DESC
            """
            return Database.execute_query(query, fetch=True)
        except Exception as e:
            logger.error(f"Error get_all: {e}")
            return []