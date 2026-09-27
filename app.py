import os
import sqlite3

from flask import Flask, render_template, request, redirect

app = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")
SQLITE_DATABASE = "cloud_lab.db"


def get_db_connection():
    if DATABASE_URL:
        import psycopg2
        from psycopg2.extras import RealDictCursor

        return psycopg2.connect(
            DATABASE_URL,
            cursor_factory=RealDictCursor
        )

    connection = sqlite3.connect(SQLITE_DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    connection = get_db_connection()

    if DATABASE_URL:
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        connection.commit()
        cursor.close()

    else:
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

        if DATABASE_URL:
            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO messages (name, message)
                VALUES (%s, %s)
                """,
                (name, message)
            )

            connection.commit()
            cursor.close()

        else:
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

    if DATABASE_URL:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT id, name, message, created_at
            FROM messages
            ORDER BY created_at DESC
        """)

        messages = cursor.fetchall()
        cursor.close()

    else:
        messages = connection.execute("""
            SELECT id, name, message, created_at
            FROM messages
            ORDER BY created_at DESC
        """).fetchall()

    connection.close()

    return render_template("index.html", messages=messages)


@app.route("/health")
def health():
    return {"status": "ok"}


init_db()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)