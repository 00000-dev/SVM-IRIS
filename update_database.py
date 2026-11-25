
import os
import psycopg


# =========================================================
# KẾT NỐI POSTGRESQL RENDER
# =========================================================

password = os.getenv("RENDER_DB_PASSWORD")
if not password:
    raise RuntimeError(
        "Chưa thiết lập biến môi trường RENDER_DB_PASSWORD"
    )

print(">>> Đang kết nối PostgreSQL Render...")

conn = psycopg.connect(
    host="dpg-dbkltqrncjis73emv1sg-a.oregon-postgres.render.com",
    port=5432,
    dbname="iris_botanica_db_new",
    user="iris_botanica_db_new_user",
    password=password,
    sslmode="require"
)

try:
    with conn.cursor() as cursor:

        # Kiểm tra bảng nguoi_dung
        cursor.execute("""
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = 'public'
                  AND table_name = 'nguoi_dung'
            )
        """)

        table_exists = cursor.fetchone()[0]

        if not table_exists:
            raise RuntimeError(
                "Không tìm thấy bảng nguoi_dung. "
                "Đã dừng để bảo vệ dữ liệu."
            )

        # Kiểm tra cột vai_tro
        cursor.execute("""
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND table_name = 'nguoi_dung'
                  AND column_name = 'vai_tro'
            )
        """)

        column_exists = cursor.fetchone()[0]

        if not column_exists:
            print(">>> Đang bổ sung cột vai_tro...")

            cursor.execute("""
                ALTER TABLE public.nguoi_dung
                ADD COLUMN vai_tro VARCHAR(20)
                NOT NULL DEFAULT 'user'
            """)

            print(">>> Đã thêm cột vai_tro.")

        else:
            print(">>> Cột vai_tro đã tồn tại, không thêm lại.")

        # Kiểm tra kết quả
        cursor.execute("""
            SELECT vai_tro, COUNT(*)
            FROM public.nguoi_dung
            GROUP BY vai_tro
            ORDER BY vai_tro
        """)

        print("\n>>> THỐNG KÊ TÀI KHOẢN:")

        for role, total in cursor.fetchall():
            print(f"{role}: {total} tài khoản")

    conn.commit()

    print("\n>>> CẬP NHẬT DATABASE THÀNH CÔNG!")

except Exception:
    conn.rollback()
    raise

finally:
    conn.close()
