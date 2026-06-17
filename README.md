# Expense Tracker MCP Server

A production-ready Model Context Protocol (MCP) server built using the modern **FastMCP** framework. This server exposes secure, asynchronous tools and data resources to LLMs (like Claude), allowing them to dynamically log, manage, and analyze personal or business expenses using an underlying SQLite database.

## 🚀 Features
- **Asynchronous Database Handlers:** Uses `aiosqlite` to ensure non-blocking, efficient database queries during concurrent AI transactions.
- **AI-Native Tools:** Exposes 3 core atomic tools designed for LLM tool-calling:
  - `add_expense`: Adds a new item with date, amount, category, subcategory, and notes.
  - `list_expenses`: Retrieves raw expense logs filtered within a precise date range.
  - `summarize`: Provides aggregated insights, grouping total spendings and counts by category.
- **Dynamic Context Resources:** Exposes a custom protocol resource (`expense://categories`) that serves a deeply structured list of main categories and subcategories, allowing the LLM to validate inputs before executing tools.
- **Cloud & Deployment Safe:** Dynamically resolves DB paths (`/tmp/expenses.db`) and ports via environment variables, making it ready for cloud hosting or local deployment.

## 🛠️ Tech Stack
- **Language:** Python
- **MCP Framework:** FastMCP (by Anthropic)
- **Database:** SQLite (via `aiosqlite` & `sqlite3`)
- **Data Format:** JSON (for category schemas)

## 📦 How to Run

### 1. Clone the Repository
```bash
git clone [https://github.com/saqiamin22-max/YOUR_REPO_NAME.git](https://github.com/saqiamin22-max/YOUR_REPO_NAME.git)
cd YOUR_REPO_NAME
