
from sqlalchemy import text
from database.connection import engine

try:
    with engine.begin() as conn:

        # Kiểm tra cột vai_tro đã tồn tại chưa
        check = conn.execute(text("""
            SELECT COUNT(*)
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = 'nguoi_dung'
              AND COLUMN_NAME = 'vai_tro'
        """)).scalar()

        if check == 0:
            conn.execute(text("""
                ALTER TABLE nguoi_dung
                ADD vai_tro VARCHAR(20) NOT NULL
                CONSTRAINT DF_nguoi_dung_vai_tro
                DEFAULT 'user' WITH VALUES
            """))
            print("Da them cot vai_tro!")

        else:
            print("Cot vai_tro da ton tai!")

        # Cấp quyền Admin cho tài khoản thao
        conn.execute(text("""
            UPDATE nguoi_dung
            SET vai_tro = 'admin'
            WHERE ten_dang_nhap = 'thao'
        """))

        print("Da cap quyen Admin cho thao!")

        # Các tài khoản còn lại giữ quyền user
        conn.execute(text("""
            UPDATE nguoi_dung
            SET vai_tro = 'user'
            WHERE vai_tro IS NULL OR vai_tro = ''
        """))

    print("\nCAP NHAT DATABASE THANH CONG!")

except Exception as e:
    print("LOI:", e)
