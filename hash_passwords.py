# ============================================
# hash_passwords.py - Simpan di root folder
# Jalankan sekali untuk hash semua password
# ============================================
"""
Script untuk hash password user di database
Jalankan dengan: python hash_passwords.py
"""

import bcrypt
import mysql.connector
from config.settings import Settings

def hash_password(password: str) -> str:
    """Hash password menggunakan bcrypt"""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def update_passwords():
    """Update semua password di database dengan versi ter-hash"""
    
    # Data user dengan password plain text
    users = [
        (1, '12345'),       # admin
        (2, 'mua123'),      # MUA Rani
        (3, 'tia123'),      # MUA Tia
        (4, 'kasir123'),    # Kasir Dita
        (5, 'lina123'),     # Owner Lina
    ]
    
    try:
        # Connect ke database
        conn = mysql.connector.connect(
            host=Settings.DB_HOST,
            port=Settings.DB_PORT,
            database=Settings.DB_NAME,
            user=Settings.DB_USER,
            password=Settings.DB_PASSWORD
        )
        cursor = conn.cursor()
        
        print("🔐 Memulai proses hashing password...")
        print("-" * 50)
        
        for user_id, plain_password in users:
            # Hash password
            hashed = hash_password(plain_password)
            
            # Update di database
            query = "UPDATE user SET password = %s WHERE id_user = %s"
            cursor.execute(query, (hashed, user_id))
            
            # Get username untuk display
            cursor.execute("SELECT username FROM user WHERE id_user = %s", (user_id,))
            result = cursor.fetchone()
            username = result[0] if result else "Unknown"
            
            print(f"✅ Updated: {username} (ID: {user_id})")
        
        # Commit changes
        conn.commit()
        print("-" * 50)
        print("✅ Semua password berhasil di-hash!")
        print()
        print("📝 Credentials untuk login:")
        print("   Admin    : sinta_admin / 12345")
        print("   MUA      : rani_mua / mua123")
        print("   Kasir    : dita_kasir / kasir123")
        print("   Owner    : lina_owner / lina123")
        
    except mysql.connector.Error as e:
        print(f"❌ Error: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    # Ensure directories exist
    Settings.ensure_directories()
    
    # Hash passwords
    update_passwords()