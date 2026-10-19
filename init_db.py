
from db import get_db_connection


def initialize_database():
    """Create the tables required by the feedback application."""

    create_tables_sql = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        role VARCHAR(10) NOT NULL
            CHECK (role IN ('student', 'staff', 'admin'))
    );

    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        category VARCHAR(100) NOT NULL,
        question_text TEXT NOT NULL,
        question_order INTEGER NOT NULL,
        UNIQUE (category, question_order)
    );

    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        student_id INTEGER NOT NULL REFERENCES users(id),
        submitted_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        is_simulated BOOLEAN NOT NULL DEFAULT FALSE
    );

    CREATE TABLE IF NOT EXISTS feedback_answers (
        id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        feedback_id INTEGER NOT NULL
            REFERENCES feedback(id) ON DELETE CASCADE,
        question_id INTEGER NOT NULL REFERENCES questions(id),
        rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
        UNIQUE (feedback_id, question_id)
    );
    """

    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(create_tables_sql)

    print("Database tables created successfully!")


if __name__ == "__main__":
    try:
        initialize_database()
    except Exception as error:
        print("Database initialization failed.")
        print("Error type:", type(error).__name__)
        print("Details:", error)
