
from db import get_db_connection

with get_db_connection() as connection:
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT role, COUNT(*)
            FROM users
            GROUP BY role
            ORDER BY role;
        """)

        results = cursor.fetchall()

print("Account verification:")

for role, count in results:
    print(f"{role}: {count}")

with get_db_connection() as connection:
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM users;")
        total = cursor.fetchone()[0]

print(f"Total accounts: {total}")
