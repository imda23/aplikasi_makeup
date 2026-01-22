"""Jadwal service"""
from config.database import Database
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)

class JadwalService:
    def get_all(self) -> List[Dict]:
        try:
            query = """
                SELECT j.*, p.nama as nama_pelanggan, u.nama_user as nama_mua
                FROM jadwal j
                JOIN pelanggan p ON j.id_pelanggan = p.id_pelanggan
                JOIN user u ON j.id_user = u.id_user
                ORDER BY j.tanggal_booking DESC, j.jam_mulai DESC
            """
            return Database.execute_query(query, fetch=True)
        except Exception as e:
            logger.error(f"Error get_all: {e}")
            return []