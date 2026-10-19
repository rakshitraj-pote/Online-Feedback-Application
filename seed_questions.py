
from db import get_db_connection


QUESTIONS = {
    "Examination Facilities": [
        "How would you rate the cleanliness of the examination room?",
        "How would you rate the seating arrangements?",
        "How would you rate the lighting in the examination room?",
        "How would you rate the ventilation in the examination room?",
        "How would you rate the availability of drinking water?",
        "How would you rate the cleanliness of the washrooms?",
    ],
    "Examination Staff": [
        "How would you rate the helpfulness of the examination staff?",
        "How would you rate the politeness of the staff?",
        "How would you rate the staff's ability to answer your questions?",
        "How would you rate the staff's professionalism?",
        "How would you rate the staff's responsiveness to requests?",
        "How would you rate the overall conduct of the staff?",
    ],
    "Examination Process": [
        "How would you rate the registration process?",
        "How would you rate the identity verification process?",
        "How would you rate the clarity of the examination instructions?",
        "How would you rate the process of entering the examination hall?",
        "How would you rate the management of examination materials?",
        "How would you rate the overall organization of the examination?",
    ],
    "Time Management": [
        "How would you rate the punctuality of the examination start?",
        "How would you rate the time taken for entry and verification?",
        "How would you rate the management of examination breaks, if any?",
        "How would you rate the communication of time limits?",
        "How would you rate the handling of delays?",
        "How would you rate the overall management of examination time?",
    ],
    "Safety and Security": [
        "How would you rate the security arrangements at the center?",
        "How would you rate the checking process at entry?",
        "How would you rate the safety of your belongings?",
        "How would you rate the clarity of emergency instructions?",
        "How would you rate the availability of assistance when needed?",
        "How would you rate your overall sense of safety at the center?",
    ],
}


def seed_questions():
    """Insert the feedback questions without creating duplicates."""

    insert_sql = """
        INSERT INTO questions (category, question_text, question_order)
        VALUES (%s, %s, %s)
        ON CONFLICT (category, question_order) DO NOTHING;
    """

    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            for category, questions in QUESTIONS.items():
                for order, question_text in enumerate(questions, start=1):
                    cursor.execute(
                        insert_sql,
                        (category, question_text, order),
                    )

    print("Feedback questions added successfully!")
    print("Expected total: 30 questions across 5 categories.")


if __name__ == "__main__":
    try:
        seed_questions()
    except Exception as error:
        print("Question seeding failed.")
        print("Error type:", type(error).__name__)
        print("Details:", error)
