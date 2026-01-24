"""
Konstanta aplikasi yang digunakan di seluruh sistem
"""

# Status Jadwal
# Status Jadwal
class StatusJadwal:
    MENUNGGU = "Menunggu"
    PROSES = "Proses"
    SELESAI = "Selesai"
    
    @staticmethod
    def get_all():
        return [
            StatusJadwal.MENUNGGU,
            StatusJadwal.PROSES,
            StatusJadwal.SELESAI
        ]

# Status Pembayaran
class StatusPembayaran:
    LUNAS = "Lunas"
    BELUM_LUNAS = "Belum Lunas"
    DP = "DP (Down Payment)"
    
    @staticmethod
    def get_all():
        return [
            StatusPembayaran.LUNAS,
            StatusPembayaran.BELUM_LUNAS,
            StatusPembayaran.DP
        ]

# Metode Pembayaran
class MetodePembayaran:
    CASH = "Cash"
    TRANSFER = "Transfer Bank"
    EWALLET = "E-Wallet (GoPay/OVO/Dana)"
    CARD = "Debit/Credit Card"
    
    @staticmethod
    def get_all():
        return [
            MetodePembayaran.CASH,
            MetodePembayaran.TRANSFER,
            MetodePembayaran.EWALLET,
            MetodePembayaran.CARD
        ]

# Role User
class UserRole:
    ADMIN = "admin"
    MAKEUP_ARTIST = "makeup_artist"
    KASIR = "kasir"
    OWNER = "owner"
    
    @staticmethod
    def get_all():
        return [
            UserRole.ADMIN,
            UserRole.MAKEUP_ARTIST,
            UserRole.KASIR,
            UserRole.OWNER
        ]