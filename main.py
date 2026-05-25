from fastmcp import FastMCP
import os
import sqlite3
import aiosqlite
import json

# -----------------------------
# CONFIG (CLOUD SAFE)
# -----------------------------
BASE_DIR = os.path.dirname(__file__)

# IMPORTANT FIX: cloud-safe DB path
DB_PATH = os.getenv("DB_PATH", "/tmp/expenses.db")

CATEGORIES_PATH = os.path.join(BASE_DIR, "categories.json")

print("DB PATH:", DB_PATH)

mcp = FastMCP("ExpenseTracker")

# -----------------------------
# INIT DB
# -----------------------------
def init_db():
    with sqlite3.connect(DB_PATH) as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT DEFAULT '',
                note TEXT DEFAULT ''
            )
        """)
        db.commit()

    print("Database ready")

init_db()

# -----------------------------
# TOOL 1: ADD EXPENSE
# -----------------------------
@mcp.tool()
async def add_expense(date, amount, category, subcategory="", note=""):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            """
            INSERT INTO expenses(date, amount, category, subcategory, note)
            VALUES (?, ?, ?, ?, ?)
            """,
            (date, amount, category, subcategory, note)
        )
        await db.commit()

        return {
            "status": "ok",
            "id": cur.lastrowid
        }

# -----------------------------
# TOOL 2: LIST EXPENSES
# -----------------------------
@mcp.tool()
async def list_expenses(start_date, end_date):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            """
            SELECT id, date, amount, category, subcategory, note
            FROM expenses
            WHERE date BETWEEN ? AND ?
            ORDER BY date DESC
            """,
            (start_date, end_date)
        )

        rows = await cur.fetchall()

        return [
            {
                "id": r[0],
                "date": r[1],
                "amount": r[2],
                "category": r[3],
                "subcategory": r[4],
                "note": r[5],
            }
            for r in rows
        ]

# -----------------------------
# TOOL 3: SUMMARY
# -----------------------------
@mcp.tool()
async def summarize(start_date, end_date, category=None):
    async with aiosqlite.connect(DB_PATH) as db:

        query = """
            SELECT category, SUM(amount), COUNT(*)
            FROM expenses
            WHERE date BETWEEN ? AND ?
        """

        params = [start_date, end_date]

        if category:
            query += " AND category = ?"
            params.append(category)

        query += " GROUP BY category ORDER BY SUM(amount) DESC"

        cur = await db.execute(query, params)
        rows = await cur.fetchall()

        return [
            {
                "category": r[0],
                "total": r[1],
                "count": r[2]
            }
            for r in rows
        ]

# -----------------------------
# RESOURCE
# -----------------------------
@mcp.resource("expense://categories", mime_type="application/json")
def categories():
    default_categories = {
        "categories": [
            "Food & Dining",
            "Transportation",
            "Shopping",
            "Entertainment",
            "Bills & Utilities",
            "Healthcare",
            "Travel",
            "Education",
            "Business",
            "Other"
        ]
    }

    try:
        with open(CATEGORIES_PATH, "r", encoding="utf-8") as f:
            return f.read()
    except:
        return json.dumps(default_categories, indent=2)

# -----------------------------
# RUN SERVER (DEPLOY SAFE)
# -----------------------------
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))

    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=port
    )