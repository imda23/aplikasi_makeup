"""
Input validation functions
"""
import re
from datetime import datetime, time, date
from typing import Tuple


class Validators:
    """Kumpulan fungsi validasi input"""
    
    @staticmethod
    def validate_required(value, field_name: str) -> Tuple[bool, str]:
        """Validasi field wajib diisi"""
        if value is None or str(value).strip() == "":
            return False, f"{field_name} wajib diisi"
        return True, ""
    
    @staticmethod
    def validate_phone(phone: str) -> Tuple[bool, str]:
        """
        Validasi nomor HP Indonesia
        Format: 08xxxxxxxxxx atau 62xxxxxxxxxx
        """
        # Hapus spasi dan dash
        phone = phone.replace(" ", "").replace("-", "")
        
        # Cek apakah semua digit
        if not phone.isdigit():
            return False, "Nomor HP harus berupa angka"
        
        # Cek panjang (10-13 digit)
        if len(phone) < 10 or len(phone) > 13:
            return False, "Nomor HP harus 10-13 digit"
        
        # Cek prefix
        if not (phone.startswith('08') or phone.startswith('62')):
            return False, "Nomor HP harus diawali 08 atau 62"
        
        return True, ""
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """Validasi format email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(pattern, email):
            return True, ""
        return False, "Format email tidak valid"
    
    @staticmethod
    def validate_positive_number(value: float, field_name: str) -> Tuple[bool, str]:
        """Validasi angka positif"""
        try:
            num = float(value)
            if num <= 0:
                return False, f"{field_name} harus lebih besar dari 0"
            return True, ""
        except (ValueError, TypeError):
            return False, f"{field_name} harus berupa angka"
    
    @staticmethod
    def validate_time_range(start_time: time, end_time: time) -> Tuple[bool, str]:
        """Validasi range waktu"""
        if start_time >= end_time:
            return False, "Jam selesai harus lebih besar dari jam mulai"
        return True, ""
    
    @staticmethod
    def validate_date_not_past(selected_date: date) -> Tuple[bool, str]:
        """Validasi tanggal tidak boleh masa lalu"""
        today = date.today()
        if selected_date < today:
            return False, "Tanggal tidak boleh di masa lalu"
        return True, ""