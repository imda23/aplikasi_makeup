"""
Database connection dan query executor
"""
import mysql.connector
from mysql.connector import Error, pooling
from config.settings import Settings
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Settings.LOGS_DIR / 'app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class Database:
    """Singleton class untuk database connection pool"""
    
    _connection_pool = None
    
    @classmethod
    def initialize_pool(cls):
        """
        Initialize connection pool
        Hanya dipanggil sekali saat aplikasi start
        """
        try:
            cls._connection_pool = pooling.MySQLConnectionPool(
                pool_name="makeup_pool",
                pool_size=5,
                pool_reset_session=True,
                host=Settings.DB_HOST,
                port=Settings.DB_PORT,
                database=Settings.DB_NAME,
                user=Settings.DB_USER,
                password=Settings.DB_PASSWORD,
                autocommit=False
            )
            logger.info("✅ Database connection pool initialized successfully")
            return True
        except Error as e:
            logger.error(f"❌ Error initializing database pool: {e}")
            return False
    
    @classmethod
    def get_connection(cls):
        """Get connection from pool"""
        if cls._connection_pool is None:
            if not cls.initialize_pool():
                raise Exception("Failed to initialize database connection pool")
        return cls._connection_pool.get_connection()
    
    @classmethod
    def execute_query(cls, query, params=None, fetch=False):
        """
        Execute SQL query dengan parameterized statement
        
        Args:
            query (str): SQL query dengan %s placeholders
            params (tuple): Parameter untuk query
            fetch (bool): True untuk SELECT, False untuk INSERT/UPDATE/DELETE
        
        Returns:
            list: Untuk fetch=True, return list of dict
            int: Untuk fetch=False, return lastrowid atau rowcount
        """
        conn = None
        cursor = None
        try:
            conn = cls.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Execute query
            cursor.execute(query, params or ())
            
            if fetch:
                # SELECT query
                result = cursor.fetchall()
                return result
            else:
                # INSERT/UPDATE/DELETE query
                conn.commit()
                # Return lastrowid untuk INSERT, rowcount untuk UPDATE/DELETE
                return cursor.lastrowid if cursor.lastrowid else cursor.rowcount
                
        except Error as e:
            if conn:
                conn.rollback()
            logger.error(f"❌ Database error: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    @classmethod
    def test_connection(cls):
        """Test database connection"""
        try:
            query = "SELECT 1 as test"
            result = cls.execute_query(query, fetch=True)
            if result and result[0]['test'] == 1:
                logger.info("✅ Database connection test successful")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Database connection test failed: {e}")
            return False