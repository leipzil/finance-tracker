from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import date

app = Flask(__name__)
DB = "finance.db"


def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,           -- 'income' or 'expense'
            category TEXT NOT NULL,
            description TEXT,
            amount REAL NOT NULL,
            date TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


@app.route("/")
def index():
    conn = get_db()
    transactions = conn.execute(
        "SELECT * FROM transactions ORDER BY date DESC, id DESC"
    ).fetchall()

    income = sum(t["amount"] for t in transactions if t["type"] == "income")
    expense = sum(t["amount"] for t in transactions if t["type"] == "expense")
    balance = income - expense

    # For the category breakdown chart (stretch goal)
    categories = {}
    for t in transactions:
        if t["type"] == "expense":
            categories[t["category"]] = categories.get(t["category"], 0) + t["amount"]

    conn.close()
    return render_template(
        "index.html",
        transactions=transactions,
        income=income,
        expense=expense,
        balance=balance,
        categories=categories,
        today=date.today().isoformat(),
    )


@app.route("/add", methods=["POST"])
def add():
    t_type = request.form["type"]
    category = request.form["category"]
    description = request.form.get("description", "")
    amount = float(request.form["amount"])
    t_date = request.form["date"]

    conn = get_db()
    conn.execute(
        "INSERT INTO transactions (type, category, description, amount, date) VALUES (?, ?, ?, ?, ?)",
        (t_type, category, description, amount, t_date),
    )
    conn.commit()
    conn.close()
    return redirect(url_for("index"))


@app.route("/delete/<int:t_id>", methods=["POST"])
def delete(t_id):
    conn = get_db()
    conn.execute("DELETE FROM transactions WHERE id = ?", (t_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
