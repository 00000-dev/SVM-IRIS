import sqlite3

DATABASE = "iris_database.db"


def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def create_model_evaluation_table():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ket_qua_mo_hinh (
            ma_mo_hinh INTEGER PRIMARY KEY AUTOINCREMENT,
            ten_mo_hinh TEXT NOT NULL UNIQUE,
            accuracy REAL NOT NULL,
            precision REAL NOT NULL,
            recall REAL NOT NULL,
            f1_score REAL NOT NULL,
            thoi_gian_huan_luyen REAL,
            thoi_gian_du_doan REAL
        )
    """)

    conn.commit()
    conn.close()
create_model_evaluation_table()