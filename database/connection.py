import os

from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


# =========================
# 1. KIỂM TRA DATABASE_URL
# =========================

DATABASE_URL = os.getenv("DATABASE_URL")


# =========================
# 2. KẾT NỐI DATABASE
# =========================

if DATABASE_URL:

    # Render PostgreSQL
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace(
            "postgres://",
            "postgresql+psycopg://",
            1
        )

    elif DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace(
            "postgresql://",
            "postgresql+psycopg://",
            1
        )

    engine = create_engine(
        DATABASE_URL,
        echo=False,
        pool_pre_ping=True
    )

else:

    # SQL Server chạy trên máy local
    server = r"judieeee\SQLEXPRESS"
    database = "IrisBotanicaDB"

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

    engine = create_engine(
        connection_url,
        echo=False,
        pool_pre_ping=True
    )


# =========================
# 3. KIỂM TRA KẾT NỐI
# =========================

def test_connection():

    try:

        with engine.connect() as connection:

            if DATABASE_URL:

                result = connection.execute(
                    text("SELECT current_database()")
                )

                database_name = result.scalar()

                print("Kết nối PostgreSQL thành công!")
                print("Database:", database_name)

            else:

                result = connection.execute(
                    text("SELECT DB_NAME()")
                )

                database_name = result.scalar()

                print("Kết nối SQL Server thành công!")
                print("Database:", database_name)

    except Exception as e:

        print("Kết nối Database thất bại!")
        print("Lỗi:", e)


if __name__ == "__main__":
    test_connection()
