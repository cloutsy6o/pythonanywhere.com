import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASS'),
            charset='utf8mb4',
            autocommit=True
        )

        if connection.is_connected():
            return connection

    except Error as e:
        print(f"❌ Verbindung fehlgeschlagen: {e}")
        return None

# Global connection instance
pdo = get_db_connection()
