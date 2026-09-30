import os
import psycopg

SQL_FILE = "SQL/irisbotanica_postgresql.sql"

password = os.getenv("RENDER_DB_PASSWORD")

if not password:
    raise RuntimeError("Chưa có biến RENDER_DB_PASSWORD")

print(">>> Đang kết nối PostgreSQL Render...")

conn = psycopg.connect(
    host="dpg-dauhp1e0tbcc73fg2gug-a.oregon-postgres.render.com",
    port=5432,
    dbname="irisbotanica",
    user="irisbotanica_app3",
    password=password,
    sslmode="require"
)

print(">>> KẾT NỐI THÀNH CÔNG!")

with open(SQL_FILE, "r", encoding="utf-8") as f:
    sql = f.read()

# File hiện tại không có dấu ; bên trong chuỗi,
# nên có thể tách các câu lệnh bằng dấu ;
statements = [
    statement.strip()
    for statement in sql.split(";")
    if statement.strip()
]

with conn.cursor() as cur:
    for i, statement in enumerate(statements, start=1):
        print(f">>> Đang chạy câu lệnh {i}/{len(statements)}...")
        cur.execute(statement)

conn.commit()

print(">>> TẠO DATABASE SCHEMA THÀNH CÔNG!")

with conn.cursor() as cur:
    cur.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)

    tables = cur.fetchall()

print("\n>>> CÁC BẢNG HIỆN CÓ:")
for table in tables:
    print(" -", table[0])

conn.close()
