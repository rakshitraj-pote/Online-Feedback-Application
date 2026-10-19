
from db import get_db_connection

with get_db_connection() as connection:
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM questions;")
        total = cursor.fetchone()[0]

        cursor.execute("""
            SELECT category, COUNT(*)
            FROM questions
            GROUP BY category
            ORDER BY category;
        """)
        categories = cursor.fetchall()

print("Total questions:", total)
print("\nQuestions per category:")

for category, count in categories:
    print(f"{category}: {count}")
