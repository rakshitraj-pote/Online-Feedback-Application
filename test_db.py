
from db import get_db_connection

try:
    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            result = cursor.fetchone()

    print("Database connection successful!")
    print("PostgreSQL responded correctly.")

except Exception as error:
    print("Database connection failed.")
    print("Error type:", type(error).__name__)
    print("Details:", error)
