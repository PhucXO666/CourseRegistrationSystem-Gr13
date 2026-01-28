import pymysql
import sys
import os
from dotenv import load_dotenv

# Load biến môi trường
load_dotenv()

# Lấy thông tin từ .env
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', 3306))
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME = os.getenv('DB_NAME', 'BTL')

def create_database_if_not_exists():
    """Tạo database nếu chưa tồn tại"""
    print("🔧 Setting up database...")
    print(f"Host: {DB_HOST}:{DB_PORT}")
    print(f"User: {DB_USER}")
    print(f"Database: {DB_NAME}")
    
    try:
        # Bước 1: Kết nối MySQL (không chỉ định database)
        print("1. Connecting to MySQL server...")
        connection = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            charset='utf8mb4',
            autocommit=True
        )
        print("✅ Connected to MySQL server")
        
        with connection.cursor() as cursor:
            # Bước 2: Tạo database
            print(f"2. Creating database '{DB_NAME}'...")
            cursor.execute(f"""
                CREATE DATABASE IF NOT EXISTS {DB_NAME} 
                CHARACTER SET utf8mb4 
                COLLATE utf8mb4_unicode_ci
            """)
            print(f"✅ Database '{DB_NAME}' created/verified")
            
            # Bước 3: Chọn database
            cursor.execute(f"USE {DB_NAME}")
            
            # Bước 4: Kiểm tra các bảng
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"📁 Found {len(tables)} tables")
            
            # Bước 5: Hiển thị thông tin MySQL
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()[0]
            print(f"📊 MySQL Version: {version}")
        
        connection.close()
        print("\n✅ Database setup completed successfully!")
        return True
        
    except pymysql.Error as e:
        error_code = e.args[0] if len(e.args) > 0 else 'Unknown'
        error_msg = e.args[1] if len(e.args) > 1 else str(e)
        
        print(f"\n❌ ERROR {error_code}: {error_msg}")
        
        if error_code == 1045:  # Access denied
            print("\n🔧 TROUBLESHOOTING:")
            print(f"1. Kiểm tra user/password: {DB_USER}/{'*' * len(DB_PASSWORD)}")
            print("2. Thử đăng nhập thủ công:")
            print(f"   mysql -u {DB_USER} -p{DB_PASSWORD}")
            print("3. Nếu quên password root, thử:")
            print("   mysql -u root (nếu không có password)")
        elif error_code == 2003:  # Can't connect
            print("\n🔧 TROUBLESHOOTING:")
            print("1. Kiểm tra MySQL có đang chạy không")
            print("2. Kiểm tra port (mặc định 3306)")
            print("3. Với XAMPP: Mở XAMPP Control Panel → Start MySQL")
        elif error_code == 1049:  # Unknown database
            print("\n🔧 TROUBLESHOOTING:")
            print("1. Database không tồn tại")
            print("2. Chạy lại script này để tự tạo")
        
        return False

if __name__ == '__main__':
    success = create_database_if_not_exists()
    if success:
        sys.exit(0)
    else:
        sys.exit(1)