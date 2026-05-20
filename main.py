from fastmcp import FastMCP
import os
import aiosqlite
import sqlite3
import json

DB_PATH = os.path.join(os.path.dirname(__file__), "expenses.db")
CATEGORIES_PATH = os.path.join(os.path.dirname(__file__), "categories.json")

print(f"Database path: {DB_PATH}")

mcp = FastMCP("ExpenseTracker")


# ---------- INIT DB ----------
def init_db():
    with sqlite3.connect(DB_PATH) as c:
        c.execute("""
        CREATE TABLE IF NOT EXISTS expenses(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            subcategory TEXT DEFAULT '',
            note TEXT DEFAULT ''
        )
        """)
        c.commit()

init_db()


# ---------- ADD EXPENSE ----------
@mcp.tool()
async def add_expense(date: str, amount: float, category: str, subcategory: str = "", note: str = ""):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """
            INSERT INTO expenses(date, amount, category, subcategory, note)
            VALUES (?, ?, ?, ?, ?)
            """,
            (date, amount, category, subcategory, note)
        )
        await db.commit()
        return {
            "status": "success",
            "id": cursor.lastrowid
        }


# ---------- LIST EXPENSES ----------
@mcp.tool()
async def list_expenses(start_date: str, end_date: str):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        cursor = await db.execute(
            """
            SELECT * FROM expenses
            WHERE date BETWEEN ? AND ?
            ORDER BY date DESC
            """,
            (start_date, end_date)
        )

        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


# ---------- SUMMARIZE ----------
@mcp.tool()
async def summarize(start_date: str, end_date: str, category: str = None):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        query = """
            SELECT category, SUM(amount) as total_amount, COUNT(*) as count
            FROM expenses
            WHERE date BETWEEN ? AND ?
        """

        params = [start_date, end_date]

        if category:
            query += " AND category = ?"
            params.append(category)

        query += " GROUP BY category ORDER BY total_amount DESC"

        cursor = await db.execute(query, params)
        rows = await cursor.fetchall()

        return [dict(row) for row in rows]


# ---------- RESOURCE ----------
@mcp.resource("expense://categories", mime_type="application/json")
def categories():
    default_categories = {
        "categories": [
            "Food",
            "Transport",
            "Shopping",
            "Bills",
            "Health",
            "Education",
            "Travel",
            "Other"
        ]
    }

    if os.path.exists(CATEGORIES_PATH):
        with open(CATEGORIES_PATH, "r", encoding="utf-8") as f:
            return f.read()

    return json.dumps(default_categories, indent=2)


# ---------- RUN SERVER ----------
if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="127.0.0.1",
        port=8000
    )