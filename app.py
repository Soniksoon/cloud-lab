from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

DATABASE = "cloud_lab.db"


def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    connection = get_db_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()


@app.route("/", methods=["GET", "POST"])
def index():

    if request.method == "POST":

        name = request.form["name"]
        message = request.form["message"]

        connection = get_db_connection()

        connection.execute(
            """
            INSERT INTO messages (name, message)
            VALUES (?, ?)
            """,
            (name, message)
        )

        connection.commit()
        connection.close()

        return redirect("/")

    connection = get_db_connection()

    messages = connection.execute(
        """
        SELECT id, name, message, created_at
        FROM messages
        ORDER BY created_at DESC
        """
    ).fetchall()

    connection.close()

    return render_template(
        "index.html",
        messages=messages
    )


@app.route("/health")
def health():
    return {
        "status": "ok"
    }


if __name__ == "__main__":

    init_db()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )