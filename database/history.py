from sqlalchemy import text
from database.connection import engine


# =========================================================
# 1. GHI LỊCH SỬ ĐĂNG NHẬP
# =========================================================

def create_login_history(ma_nguoi_dung):
    sql = text("""
        INSERT INTO lich_su_dang_nhap (
            ma_nguoi_dung
        )
        VALUES (
            :ma_nguoi_dung
        )
    """)

    with engine.begin() as connection:
        result = connection.execute(
            sql,
            {
                "ma_nguoi_dung": ma_nguoi_dung
            }
        )

        return result.rowcount > 0


# =========================================================
# 2. LẤY LỊCH SỬ ĐĂNG NHẬP CỦA MỘT NGƯỜI DÙNG
# =========================================================

def get_login_history(ma_nguoi_dung):
    sql = text("""
        SELECT
            ma_dang_nhap,
            ma_nguoi_dung,
            thoi_gian_dang_nhap
        FROM lich_su_dang_nhap
        WHERE ma_nguoi_dung = :ma_nguoi_dung
        ORDER BY thoi_gian_dang_nhap DESC
    """)

    with engine.connect() as connection:
        result = connection.execute(
            sql,
            {
                "ma_nguoi_dung": ma_nguoi_dung
            }
        )

        history = []

        for row in result:
            history.append({
                "ma_dang_nhap": row.ma_dang_nhap,
                "ma_nguoi_dung": row.ma_nguoi_dung,
                "thoi_gian_dang_nhap": row.thoi_gian_dang_nhap
            })

        return history