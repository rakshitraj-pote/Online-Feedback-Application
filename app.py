
from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        role = request.form.get("role", "")

        return (
            f"Flask received your form! "
            f"Username: {username}. "
            f"Selected role: {role}."
        )

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
