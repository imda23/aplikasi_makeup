"""Layanan service"""
from config.database import Database
from typing import List, Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class LayananService:
    def get_all(self) -> List[Dict]:
        try:
            query = """
                SELECT l.*, k.nama_kategori 
                FROM layanan l
                JOIN kategori_layanan k ON l.id_kategori = k.id_kategori
                ORDER BY l.nama_layanan ASC
            """
            return Database.execute_query(query, fetch=True)
        except Exception as e:
            logger.error(f"Error get_all: {e}")
            return []
    
    def get_kategori_all(self) -> List[Dict]:
        try:
            query = "SELECT * FROM kategori_layanan ORDER BY nama_kategori ASC"
            return Database.execute_query(query, fetch=True)
        except Exception as e:
            logger.error(f"Error get_kategori_all: {e}")
            return []