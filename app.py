
import os

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
)

from werkzeug.security import check_password_hash

from db import get_db_connection


app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

if not app.secret_key:
    raise RuntimeError("Set FLASK_SECRET_KEY in your .env file.")


# --------------------------------------------------
# LOGIN
# --------------------------------------------------

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        selected_role = request.form.get("role", "").strip().lower()

        if selected_role not in ("student", "staff"):
            return "Invalid account type.", 400

        try:
            with get_db_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT id, username, password_hash, role
                        FROM users
                        WHERE username = %s;
                        """,
                        (username,),
                    )
                    user = cursor.fetchone()

        except Exception:
            app.logger.exception("Login database error")
            return "A database error occurred. Please try again.", 500

        if not user or not check_password_hash(user[2], password):
            return "Invalid username or password.", 401

        user_id, stored_username, _, actual_role = user

        # Only student and staff accounts can log in.
        if actual_role != selected_role:
            return "Invalid account type.", 403

        session.clear()
        session["user_id"] = user_id
        session["username"] = stored_username
        session["role"] = actual_role

        return redirect(url_for("dashboard"))

    return render_template("index.html")


# --------------------------------------------------
# ROLE-BASED DASHBOARD REDIRECT
# --------------------------------------------------

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("home"))

    role = session["role"]

    if role == "staff":
        return redirect(url_for("staff_dashboard"))

    if role == "student":
        return render_template(
            "student_dashboard.html",
            username=session["username"],
        )

    session.clear()
    return redirect(url_for("home"))


# --------------------------------------------------
# STUDENT FEEDBACK FORM AND SUBMISSION
# --------------------------------------------------

@app.route("/feedback", methods=["GET", "POST"])
def feedback():
    if "user_id" not in session:
        return redirect(url_for("home"))

    if session["role"] != "student":
        return "Students only.", 403

    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:

                # Prevent a student from submitting twice.
                cursor.execute(
                    """
                    SELECT id
                    FROM feedback
                    WHERE student_id = %s
                      AND is_simulated = FALSE;
                    """,
                    (session["user_id"],),
                )

                if cursor.fetchone():
                    return render_template(
                        "feedback_form.html",
                        questions=[],
                        already_submitted=True,
                    )

                if request.method == "POST":
                    cursor.execute(
                        "SELECT id FROM questions ORDER BY id;"
                    )
                    question_ids = [
                        row[0] for row in cursor.fetchall()
                    ]

                    if len(question_ids) != 30:
                        return (
                            "The questionnaire must contain exactly "
                            "30 questions.",
                            500,
                        )

                    ratings = []

                    for question_id in question_ids:
                        value = request.form.get(
                            f"question_{question_id}", ""
                        )

                        try:
                            rating = int(value)
                        except (ValueError, TypeError):
                            return "Please answer every question.", 400

                        if rating not in range(1, 6):
                            return "Invalid rating submitted.", 400

                        ratings.append((question_id, rating))

                    cursor.execute(
                        """
                        INSERT INTO feedback (student_id, is_simulated)
                        VALUES (%s, FALSE)
                        RETURNING id;
                        """,
                        (session["user_id"],),
                    )
                    feedback_id = cursor.fetchone()[0]

                    for question_id, rating in ratings:
                        cursor.execute(
                            """
                            INSERT INTO feedback_answers
                                (feedback_id, question_id, rating)
                            VALUES (%s, %s, %s);
                            """,
                            (feedback_id, question_id, rating),
                        )

                    return redirect(url_for("feedback_success"))

                cursor.execute(
                    """
                    SELECT id, category, question_text, question_order
                    FROM questions
                    ORDER BY
                        CASE category
                            WHEN 'Examination Facilities' THEN 1
                            WHEN 'Examination Staff' THEN 2
                            WHEN 'Examination Process' THEN 3
                            WHEN 'Time Management' THEN 4
                            WHEN 'Safety and Security' THEN 5
                            ELSE 6
                        END,
                        question_order;
                    """
                )
                questions = cursor.fetchall()

        return render_template(
            "feedback_form.html",
            questions=questions,
            already_submitted=False,
        )

    except Exception:
        app.logger.exception("Feedback processing failed")
        return "Unable to process feedback. Please try again.", 500


# --------------------------------------------------
# FEEDBACK SUCCESS PAGE
# --------------------------------------------------

@app.route("/feedback/success")
def feedback_success():
    if "user_id" not in session:
        return redirect(url_for("home"))

    if session["role"] != "student":
        return "Students only.", 403

    return render_template("feedback_success.html")


# --------------------------------------------------
# STAFF DASHBOARD
# --------------------------------------------------

@app.route("/staff")
def staff_dashboard():
    if "user_id" not in session:
        return redirect(url_for("home"))

    if session["role"] != "staff":
        return "Staff access only.", 403

    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:

                # Count genuine student submissions only.
                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM feedback
                    WHERE is_simulated = FALSE;
                    """
                )
                total_feedback = cursor.fetchone()[0]

                # Calculate average ratings from genuine feedback.
                cursor.execute(
                    """
                    SELECT
                        q.category,
                        ROUND(AVG(a.rating)::numeric, 2)
                    FROM feedback_answers a
                    JOIN questions q ON q.id = a.question_id
                    JOIN feedback f ON f.id = a.feedback_id
                    WHERE f.is_simulated = FALSE
                    GROUP BY q.category
                    ORDER BY
                        CASE q.category
                            WHEN 'Examination Facilities' THEN 1
                            WHEN 'Examination Staff' THEN 2
                            WHEN 'Examination Process' THEN 3
                            WHEN 'Time Management' THEN 4
                            WHEN 'Safety and Security' THEN 5
                            ELSE 6
                        END;
                    """
                )
                category_averages = cursor.fetchall()

        return render_template(
            "staff_dashboard.html",
            username=session["username"],
            total_feedback=total_feedback,
            category_averages=category_averages,
        )

    except Exception:
        app.logger.exception("Staff dashboard error")
        return "Unable to load the staff dashboard.", 500


# --------------------------------------------------
# LOGOUT
# --------------------------------------------------

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("home"))


# --------------------------------------------------
# RUN APPLICATION
# --------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
