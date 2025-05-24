import pyodbc

# print("Installed ODBC Drivers:")
# for driver in pyodbc.drivers():
#     print(driver)

import pyodbc

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=37.32.11.148;"
    "DATABASE=DashboardbManager;"
    "UID=sa;"
    "PWD=NsNs7605@@;"
    "Encrypt=yes;"
    "TrustServerCertificate=yes;"
    "Connection Timeout=30;"
)

try:
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    cursor.execute("SELECT TOP 10 * FROM category")  # Replace with your table
    rows = cursor.fetchall()

    for row in rows:
        print(row)

    cursor.close()
    conn.close()

except Exception as e:
    print("Database connection failed:", e)
