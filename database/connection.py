from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


# =========================
# 1. THÔNG TIN SQL SERVER
# =========================

server = r"judieeee\SQLEXPRESS"
database = "IrisBotanicaDB"


# =========================
# 2. TẠO CHUỖI KẾT NỐI
# =========================

connection_url = URL.create(
    "mssql+pyodbc",
    query={
        "driver": "ODBC Driver 18 for SQL Server",
        "trusted_connection": "yes",
        "TrustServerCertificate": "yes"
    },
    host=server,
    database=database
)


# =========================
# 3. TẠO ENGINE
# =========================

engine = create_engine(
    connection_url,
    echo=False
)


# =========================
# 4. KIỂM TRA KẾT NỐI
# =========================

def test_connection():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT DB_NAME()"))
            database_name = result.scalar()

            print("Kết nối SQL Server thành công!")
            print("Database:", database_name)

    except Exception as e:
        print("Kết nối SQL Server thất bại!")
        print("Lỗi:", e)


if __name__ == "__main__":
    test_connection()