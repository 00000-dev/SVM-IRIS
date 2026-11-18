import psycopg

conn = psycopg.connect(
    host="dpg-dauhp1e0tbcc73fg2gug-a.oregon-postgres.render.com",
    port=5432,
    dbname="irisbotanica",
    user="irisbotanica_app3",
    password="rifIUdgxng6gQXV7ZJlIY6U8iEBdtYhi",
    sslmode="require"
)

print("✅ Kết nối PostgreSQL Render thành công!")

with conn.cursor() as cur:
    cur.execute("SELECT current_database(), current_user;")
    result = cur.fetchone()
    print("Database:", result[0])
    print("User:", result[1])

conn.close()