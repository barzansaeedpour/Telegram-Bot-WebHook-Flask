from db_mssql import get_sqlserver_connection

conn = get_sqlserver_connection()
if conn:
    cursor = conn.cursor()
    cursor.execute("SELECT TOP 1 * FROM category")
    row = cursor.fetchone()
    print(row)
    conn.close()
