import os
import traceback
import psycopg

print(">>> BẮT ĐẦU TEST POSTGRESQL")

password = os.getenv("RENDER_DB_PASSWORD")

print(">>> Đã đọc biến password:", bool(password))

if not password:
    print(">>> LỖI: chưa có RENDER_DB_PASSWORD")
    raise SystemExit

try:
    print(">>> Đang kết nối Render PostgreSQL...")

    conn = psycopg.connect(
        host="dpg-dauhp1e0tbcc73fg2gug-a.oregon-postgres.render.com",
        port=5432,
        dbname="irisbotanica",
        user="irisbotanica_app3",
        password=password,
        sslmode="require",
        connect_timeout=10
    )

    print(">>> KẾT NỐI THÀNH CÔNG!")

    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT current_database(), current_user;"
        )

        result = cursor.fetchone()

        print("Database:", result[0])
        print("User:", result[1])

    conn.close()

except Exception as e:
    print(">>> KẾT NỐI THẤT BẠI!")
    print("Lỗi:", repr(e))
    traceback.print_exc()