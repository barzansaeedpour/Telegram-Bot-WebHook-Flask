import os
import pyodbc
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SERVER_NAME = os.getenv("SERVER_NAME")
DB_NAME = os.getenv("DB_NAME")
LOGIN = os.getenv("LOGIN")
PASSWORD = os.getenv("PASSWORD")

def get_sqlserver_connection(conn_str=None):
    try:
        if not conn_str:
            conn_str = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={SERVER_NAME};"
                f"DATABASE={DB_NAME};"
                f"UID={LOGIN};"
                f"PWD={PASSWORD};"
                "Encrypt=yes;"
                "TrustServerCertificate=yes;"
                "Connection Timeout=60;"
            )
        conn = pyodbc.connect(conn_str)
        print("✅ Connected to SQL Server.")
        return conn
    except Exception as e:
        print("❌ Could not connect to SQL Server.")
        print("Error:", e)
        return None
