# add_user.py
from db import SessionLocal, DashboardPageConnection

db = SessionLocal()
query = DashboardPageConnection(page_id="20228",connection_string="DRIVER={ODBC Driver 17 for SQL Server};SERVER=37.32.11.148;DATABASE=MANDEGAR20;UID=sa;PWD=NsNs7605@@;Encrypt=yes;TrustServerCertificate=yes;Connection Timeout=30;", query_title="جمع کل مانده", query="select sum(r.Value1) - sum(r.Value2) as Total  from v_Acc_VouchersRow r where r.fYear=(select max(code) from Pub_fYear)  and Cod_1=600",)
db.add(query)
db.commit()
db.close()
print("Query added.")
