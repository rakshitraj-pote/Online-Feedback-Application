
import os

from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

from db import get_db_connection


load_dotenv()


def seed_users():
    users = []

    # Prepare 300 student accounts.
    for number in range(1, 301):
        users.append((
            f"StudentName{number}",
            f"StudentPass{number}",
            "student",
        ))

    # Prepare 3 staff accounts.
    for number in range(1, 4):
        users.append((
            f"StaffName{number}",
            f"StaffPass{number}",
            "staff",
        ))

    # Read the admin credentials from .env.
    admin_username = os.getenv("ADMIN_USERNAME", "Admin")
    admin_password = os.getenv("ADMIN_PASSWORD")

    if not admin_password:
        raise RuntimeError(
            "Set ADMIN_PASSWORD in your .env file before running this script."
        )

    users.append((admin_username, admin_password, "admin"))

    insert_sql = """
        INSERT INTO users (username, password_hash, role)
        VALUES (%s, %s, %s)
        ON CONFLICT (username) DO NOTHING;
    """

    total = len(users)
    inserted = 0

    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            for number, (username, password, role) in enumerate(users, start=1):
                cursor.execute(
                    "SELECT 1 FROM users WHERE username = %s;",
                    (username,),
                )

                if cursor.fetchone():
                    continue

                password_hash = generate_password_hash(password)

                cursor.execute(
                    insert_sql,
                    (username, password_hash, role),
                )

                inserted += 1

                if number % 25 == 0 or number == total:
                    print(f"Progress: checked {number}/{total} accounts.")

    print("User seeding completed!")
    print(f"New accounts created: {inserted}")
    print("Student accounts configured: 300")
    print("Staff accounts configured: 3")
    print("Admin account configured: 1")


if __name__ == "__main__":
    try:
        seed_users()
    except Exception as error:
        print("User seeding failed.")
        print("Error type:", type(error).__name__)
        print("Details:", error)
