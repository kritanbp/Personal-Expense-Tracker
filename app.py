"""
Personal Expense Tracker
-------------------------
A simple Flask web app for tracking income and expenses.
Uses SQLite3 for storage, Pandas for data analysis, and
Matplotlib for generating spending charts.
"""

import os
import sqlite3
from datetime import datetime, date

import matplotlib
matplotlib.use("Agg")  # non-interactive backend, needed for server-side chart generation
import matplotlib.pyplot as plt
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, flash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "expenses.db")
CHART_PATH = os.path.join(BASE_DIR, "static", "chart.png")

app = Flask(__name__)
app.secret_key = "change-this-secret-key"  # needed for flash messages

CATEGORIES = [
    "Food", "Transport", "Housing", "Utilities", "Entertainment",
    "Health", "Shopping", "Salary", "Other"
]


# ---------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the transactions table if it doesn't already exist."""
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            type TEXT NOT NULL CHECK(type IN ('Income', 'Expense')),
            category TEXT NOT NULL,
            description TEXT,
            amount REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------
@app.route("/")
def index():
    conn = get_db_connection()
    transactions = conn.execute(
        "SELECT * FROM transactions ORDER BY date DESC, id DESC"
    ).fetchall()
    conn.close()

    # Use pandas to compute quick summary stats
    df = pd.DataFrame(transactions, columns=transactions[0].keys()) if transactions else pd.DataFrame(
        columns=["id", "date", "type", "category", "description", "amount"]
    )

    total_income = df.loc[df["type"] == "Income", "amount"].sum() if not df.empty else 0
    total_expense = df.loc[df["type"] == "Expense", "amount"].sum() if not df.empty else 0
    balance = total_income - total_expense

    return render_template(
        "index.html",
        transactions=transactions,
        total_income=total_income,
        total_expense=total_expense,
        balance=balance,
    )


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        tx_date = request.form.get("date") or date.today().isoformat()
        tx_type = request.form.get("type")
        category = request.form.get("category")
        description = request.form.get("description", "").strip()
        amount = request.form.get("amount")

        # Basic validation
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError
        except (TypeError, ValueError):
            flash("Please enter a valid positive amount.", "error")
            return redirect(url_for("add"))

        if tx_type not in ("Income", "Expense") or not category:
            flash("Please choose a valid type and category.", "error")
            return redirect(url_for("add"))

        conn = get_db_connection()
        conn.execute(
            "INSERT INTO transactions (date, type, category, description, amount) "
            "VALUES (?, ?, ?, ?, ?)",
            (tx_date, tx_type, category, description, amount),
        )
        conn.commit()
        conn.close()

        flash("Transaction added successfully.", "success")
        return redirect(url_for("index"))

    return render_template("add_edit.html", categories=CATEGORIES, transaction=None, today=date.today().isoformat())


@app.route("/edit/<int:tx_id>", methods=["GET", "POST"])
def edit(tx_id):
    conn = get_db_connection()
    transaction = conn.execute("SELECT * FROM transactions WHERE id = ?", (tx_id,)).fetchone()

    if transaction is None:
        conn.close()
        flash("Transaction not found.", "error")
        return redirect(url_for("index"))

    if request.method == "POST":
        tx_date = request.form.get("date")
        tx_type = request.form.get("type")
        category = request.form.get("category")
        description = request.form.get("description", "").strip()
        amount = request.form.get("amount")

        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError
        except (TypeError, ValueError):
            flash("Please enter a valid positive amount.", "error")
            conn.close()
            return redirect(url_for("edit", tx_id=tx_id))

        conn.execute(
            "UPDATE transactions SET date=?, type=?, category=?, description=?, amount=? WHERE id=?",
            (tx_date, tx_type, category, description, amount, tx_id),
        )
        conn.commit()
        conn.close()

        flash("Transaction updated successfully.", "success")
        return redirect(url_for("index"))

    conn.close()
    return render_template("add_edit.html", categories=CATEGORIES, transaction=transaction, today=date.today().isoformat())


@app.route("/delete/<int:tx_id>", methods=["POST"])
def delete(tx_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM transactions WHERE id = ?", (tx_id,))
    conn.commit()
    conn.close()
    flash("Transaction deleted.", "success")
    return redirect(url_for("index"))


@app.route("/summary")
def summary():
    conn = get_db_connection()
    transactions = conn.execute("SELECT * FROM transactions").fetchall()
    conn.close()

    if not transactions:
        flash("Add some transactions first to see a summary.", "error")
        return redirect(url_for("index"))

    df = pd.DataFrame(transactions, columns=transactions[0].keys())

    total_income = df.loc[df["type"] == "Income", "amount"].sum()
    total_expense = df.loc[df["type"] == "Expense", "amount"].sum()
    balance = total_income - total_expense

    # Expenses grouped by category, for the pie chart
    expense_df = df[df["type"] == "Expense"]
    by_category = expense_df.groupby("category")["amount"].sum().sort_values(ascending=False)

    generate_chart(by_category)

    return render_template(
        "summary.html",
        total_income=total_income,
        total_expense=total_expense,
        balance=balance,
        by_category=by_category,
    )


def generate_chart(by_category: pd.Series):
    """Generate a pie chart of expenses by category and save it as a PNG."""
    plt.figure(figsize=(6, 6))
    if by_category.empty:
        plt.text(0.5, 0.5, "No expense data yet", ha="center", va="center")
        plt.axis("off")
    else:
        plt.pie(
            by_category.values,
            labels=by_category.index,
            autopct="%1.1f%%",
            startangle=90,
        )
        plt.title("Expenses by Category")
    plt.tight_layout()
    plt.savefig(CHART_PATH)
    plt.close()


if __name__ == "__main__":
    os.makedirs(os.path.join(BASE_DIR, "static"), exist_ok=True)
    init_db()
    app.run(debug=True)
