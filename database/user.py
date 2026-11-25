
from sqlalchemy import text
from database.connection import engine
from passlib.context import CryptContext


# =========================================================
# 1. CẤU HÌNH MÃ HÓA MẬT KHẨU
# =========================================================

pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto"
)


def hash_password(mat_khau):
    return pwd_context.hash(mat_khau)


def verify_password(mat_khau, mat_khau_db):
    """
    Hỗ trợ cả mật khẩu cũ dạng văn bản
    và mật khẩu mới đã được mã hóa.
    """
    try:
        if pwd_context.identify(mat_khau_db):
            return pwd_context.verify(mat_khau, mat_khau_db)

        return mat_khau == mat_khau_db

    except Exception:
        return False


# =========================================================
# 2. KIỂM TRA TÊN ĐĂNG NHẬP
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
            {"ten_dang_nhap": ten_dang_nhap}
        )
        return result.fetchone() is not None
# =========================================================
# 3. TẠO TÀI KHOẢN USER
# =========================================================

def create_user(ten_dang_nhap, mat_khau):

    ten_dang_nhap = ten_dang_nhap.strip()

    if not ten_dang_nhap or not mat_khau:
        return False

    mat_khau_ma_hoa = hash_password(mat_khau)

    sql = text("""
        INSERT INTO nguoi_dung (ten_dang_nhap, mat_khau)
        VALUES (:ten_dang_nhap, :mat_khau)
    """)

    with engine.begin() as connection:
        result = connection.execute(sql, {
            "ten_dang_nhap": ten_dang_nhap,
            "mat_khau": mat_khau_ma_hoa
        })

        return result.rowcount > 0

# =========================================================
# 4. KIỂM TRA ĐĂNG NHẬP
# =========================================================

def check_login(ten_dang_nhap, mat_khau):
    sql = text("""
       SELECT
    ma_nguoi_dung,
    ten_dang_nhap,
    mat_khau,
    trang_thai,
    vai_tro
FROM nguoi_dung
WHERE ten_dang_nhap = :ten_dang_nhap
    """)

    with engine.begin() as connection:
        user = connection.execute(
            sql,
            {"ten_dang_nhap": ten_dang_nhap}
        ).fetchone()

        if user is None:
            return None

        if not user.trang_thai:
            return None

        if not verify_password(mat_khau, user.mat_khau):
            return None

        # Tự động mã hóa lại mật khẩu cũ sau khi đăng nhập thành công
        if not pwd_context.identify(user.mat_khau):
            connection.execute(
                text("""
                    UPDATE nguoi_dung
                    SET mat_khau = :mat_khau
                    WHERE ma_nguoi_dung = :ma_nguoi_dung
                """),
                {
                    "mat_khau": hash_password(mat_khau),
                    "ma_nguoi_dung": user.ma_nguoi_dung
                }
            )

        return {
            "ma_nguoi_dung": user.ma_nguoi_dung,
            "ten_dang_nhap": user.ten_dang_nhap,
            "vai_tro": user.vai_tro
        }


# =========================================================
# 5. LẤY THÔNG TIN MỘT NGƯỜI DÙNG
# =========================================================

def get_user_by_id(ma_nguoi_dung):
    sql = text("""
        SELECT
            ma_nguoi_dung,
            ten_dang_nhap,
            ngay_tao,
            trang_thai,
            vai_tro
        FROM nguoi_dung
        WHERE ma_nguoi_dung = :ma_nguoi_dung
    """)

    with engine.connect() as connection:
        user = connection.execute(
            sql,
            {"ma_nguoi_dung": ma_nguoi_dung}
        ).fetchone()

        if user is None:
            return None

        return {
            "ma_nguoi_dung": user.ma_nguoi_dung,
            "ten_dang_nhap": user.ten_dang_nhap,
            "ngay_tao": user.ngay_tao,
            "trang_thai": user.trang_thai,
            "vai_tro": user.vai_tro
        }


# =========================================================
# 6. ADMIN: LẤY DANH SÁCH TÀI KHOẢN
# =========================================================

def get_all_users():
    sql = text("""
        SELECT
            ma_nguoi_dung,
            ten_dang_nhap,
            ngay_tao,
            trang_thai,
            vai_tro
        FROM nguoi_dung
        ORDER BY ngay_tao DESC
    """)

    with engine.connect() as connection:
        result = connection.execute(sql)

        return [
            {
                "ma_nguoi_dung": row.ma_nguoi_dung,
                "ten_dang_nhap": row.ten_dang_nhap,
                "ngay_tao": row.ngay_tao,
                "trang_thai": row.trang_thai,
                "vai_tro": row.vai_tro
            }
            for row in result
        ]


# =========================================================
# 7. ADMIN: KHÓA / MỞ KHÓA TÀI KHOẢN USER
# =========================================================

def update_user_status(ma_nguoi_dung, trang_thai):
    sql = text("""
        UPDATE nguoi_dung
        SET trang_thai = :trang_thai
        WHERE ma_nguoi_dung = :ma_nguoi_dung
          AND vai_tro = 'user'
    """)

    with engine.begin() as connection:
        result = connection.execute(sql, {
            "ma_nguoi_dung": ma_nguoi_dung,
            "trang_thai": trang_thai
        })

        return result.rowcount > 0
