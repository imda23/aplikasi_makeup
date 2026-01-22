"""
Formatting utility functions
"""
from datetime import datetime, date, time
from typing import Union


class Formatters:
    """Helper class untuk formatting data"""
    
    @staticmethod
    def format_currency(amount: Union[int, float, str]) -> str:
        """
        Format angka menjadi format Rupiah
        
        Args:
            amount: Jumlah dalam angka
            
        Returns:
            String format Rupiah (contoh: Rp 1.500.000)
        """
        try:
            # Convert to float
            if isinstance(amount, str):
                amount = float(amount.replace(',', ''))
            else:
                amount = float(amount)
            
            # Format dengan separator titik
            formatted = f"{amount:,.0f}".replace(',', '.')
            return f"Rp {formatted}"
        except (ValueError, TypeError):
            return "Rp 0"
    
    @staticmethod
    def format_date(date_obj: Union[date, datetime, str]) -> str:
        """
        Format tanggal ke format Indonesia
        
        Args:
            date_obj: Object date/datetime atau string
            
        Returns:
            String format tanggal (contoh: 16 Oktober 2025)
        """
        try:
            if isinstance(date_obj, str):
                date_obj = datetime.strptime(date_obj, '%Y-%m-%d').date()
            elif isinstance(date_obj, datetime):
                date_obj = date_obj.date()
            
            months = [
                'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
                'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'
            ]
            
            return f"{date_obj.day} {months[date_obj.month - 1]} {date_obj.year}"
        except:
            return str(date_obj)
    
    @staticmethod
    def format_time(time_obj: Union[time, str]) -> str:
        """
        Format waktu
        
        Args:
            time_obj: Object time atau string
            
        Returns:
            String format waktu (contoh: 09:00)
        """
        try:
            if isinstance(time_obj, str):
                time_obj = datetime.strptime(time_obj, '%H:%M:%S').time()
            
            return time_obj.strftime('%H:%M')
        except:
            return str(time_obj)
    
    @staticmethod
    def parse_currency(currency_str: str) -> float:
        """
        Parse string Rupiah ke float
        
        Args:
            currency_str: String format Rupiah
            
        Returns:
            Float value
        """
        try:
            # Remove Rp and dots
            cleaned = currency_str.replace('Rp', '').replace('.', '').strip()
            return float(cleaned)
        except:
            return 0.0