"""Pelanggan service"""
from config.database import Database
from typing import List, Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class PelangganService:
    def get_all(self) -> List[Dict]:
        try:
            query = "SELECT * FROM pelanggan ORDER BY nama ASC"
            return Database.execute_query(query, fetch=True)
        except Exception as e:
            logger.error(f"Error get_all: {e}")
            return []
    
    def get_by_id(self, id_pelanggan: int) -> Optional[Dict]:
        try:
            query = "SELECT * FROM pelanggan WHERE id_pelanggan = %s"
            result = Database.execute_query(query, (id_pelanggan,), fetch=True)
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Error get_by_id: {e}")
            return None
    
    def search(self, keyword: str) -> List[Dict]:
        try:
            query = """
                SELECT * FROM pelanggan 
                WHERE nama LIKE %s OR no_hp LIKE %s OR alamat LIKE %s
                ORDER BY nama ASC
            """
            param = f"%{keyword}%"
            return Database.execute_query(query, (param, param, param), fetch=True)
        except Exception as e:
            logger.error(f"Error search: {e}")
            return []
    
    def create(self, nama: str, no_hp: str, alamat: str) -> Tuple[bool, str]:
        try:
            check = "SELECT COUNT(*) as count FROM pelanggan WHERE no_hp = %s"
            result = Database.execute_query(check, (no_hp,), fetch=True)
            if result[0]['count'] > 0:
                return False, "Nomor HP sudah terdaftar"
            
            query = "INSERT INTO pelanggan (nama, no_hp, alamat) VALUES (%s, %s, %s)"
            Database.execute_query(query, (nama, no_hp, alamat))
            logger.info(f"✅ Pelanggan created: {nama}")
            return True, "Pelanggan berhasil ditambahkan"
        except Exception as e:
            logger.error(f"❌ Error create: {e}")
            return False, "Gagal menambahkan pelanggan"
    
    def update(self, id_pelanggan: int, nama: str, no_hp: str, alamat: str) -> Tuple[bool, str]:
        try:
            check = "SELECT COUNT(*) as count FROM pelanggan WHERE no_hp = %s AND id_pelanggan != %s"
            result = Database.execute_query(check, (no_hp, id_pelanggan), fetch=True)
            if result[0]['count'] > 0:
                return False, "Nomor HP sudah digunakan pelanggan lain"
            
            query = "UPDATE pelanggan SET nama=%s, no_hp=%s, alamat=%s WHERE id_pelanggan=%s"
            Database.execute_query(query, (nama, no_hp, alamat, id_pelanggan))
            logger.info(f"✅ Pelanggan updated: {id_pelanggan}")
            return True, "Pelanggan berhasil diupdate"
        except Exception as e:
            logger.error(f"❌ Error update: {e}")
            return False, "Gagal mengupdate pelanggan"
    
    def delete(self, id_pelanggan: int) -> Tuple[bool, str]:
        try:
            check = "SELECT COUNT(*) as count FROM transaksi WHERE id_pelanggan = %s"
            result = Database.execute_query(check, (id_pelanggan,), fetch=True)
            if result[0]['count'] > 0:
                return False, "Pelanggan memiliki transaksi, tidak dapat dihapus"
            
            query = "DELETE FROM pelanggan WHERE id_pelanggan = %s"
            Database.execute_query(query, (id_pelanggan,))
            logger.info(f"✅ Pelanggan deleted: {id_pelanggan}")
            return True, "Pelanggan berhasil dihapus"
        except Exception as e:
            logger.error(f"❌ Error delete: {e}")
            return False, "Gagal menghapus pelanggan"