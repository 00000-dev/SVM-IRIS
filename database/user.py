from sqlalchemy import text
from database.connection import engine


# =========================================================
# 1. KIỂM TRA TÊN ĐĂNG NHẬP ĐÃ TỒN TẠI
# =========================================================

def username_exists(ten_dang_nhap):
    sql = text("""
        SELECT ma_nguoi_dung
        FROM nguoi_dung
        WHERE ten_dang_nhap = :ten_dang_nhap
    """)

    with engine.connect() as connection:
        result = connection.execute(
            sql,
            {
                "ten_dang_nhap": ten_dang_nhap
            }
        )

        return result.fetchone() is not None


# =========================================================
# 2. TẠO TÀI KHOẢN
# =========================================================

def create_user(ten_dang_nhap, mat_khau):
    sql = text("""
        INSERT INTO nguoi_dung (
            ten_dang_nhap,
            mat_khau
        )
        VALUES (
            :ten_dang_nhap,
            :mat_khau
        )
    """)

    with engine.begin() as connection:
        result = connection.execute(
            sql,
            {
                "ten_dang_nhap": ten_dang_nhap,
                "mat_khau": mat_khau
            }
        )

        return result.rowcount > 0


# =========================================================
# 3. KIỂM TRA ĐĂNG NHẬP
# =========================================================

def check_login(ten_dang_nhap, mat_khau):
    sql = text("""
        SELECT
            ma_nguoi_dung,
            ten_dang_nhap,
            mat_khau,
            trang_thai
        FROM nguoi_dung
        WHERE ten_dang_nhap = :ten_dang_nhap
    """)

    with engine.connect() as connection:
        result = connection.execute(
            sql,
            {
                "ten_dang_nhap": ten_dang_nhap
            }
        )

        user = result.fetchone()

        # Không tìm thấy tài khoản
        if user is None:
            return None

        # Tài khoản đang bị khóa
        if not user.trang_thai:
            return None

        # Kiểm tra mật khẩu
        if user.mat_khau != mat_khau:
            return None

        return {
            "ma_nguoi_dung": user.ma_nguoi_dung,
            "ten_dang_nhap": user.ten_dang_nhap
        }


# =========================================================
# 4. LẤY THÔNG TIN NGƯỜI DÙNG
# =========================================================

def get_user_by_id(ma_nguoi_dung):
    sql = text("""
        SELECT
            ma_nguoi_dung,
            ten_dang_nhap,
            ngay_tao,
            trang_thai
        FROM nguoi_dung
        WHERE ma_nguoi_dung = :ma_nguoi_dung
    """)

    with engine.connect() as connection:
        result = connection.execute(
            sql,
            {
                "ma_nguoi_dung": ma_nguoi_dung
            }
        )

        user = result.fetchone()

        if user is None:
            return None

        return {
            "ma_nguoi_dung": user.ma_nguoi_dung,
            "ten_dang_nhap": user.ten_dang_nhap,
            "ngay_tao": user.ngay_tao,
            "trang_thai": user.trang_thai
        }