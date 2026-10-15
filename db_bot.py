"""Ask questions about the vending machine database in plain English.

Flow: question -> GPT (with schema) -> SQL -> SQLite -> GPT -> plain-English answer

Usage:
    python app.py                       # zero-shot (default)
    python app.py --strategy few-shot   # include example question/SQL pairs
"""
import argparse
import os
import sqlite3

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

MODEL = "gpt-4o-mini"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "aidb.sqlite")

# Strategy 1 (zero-shot): the schema is all the model gets.
# Foreign keys are in the schema text, and sample rows are added below.
FEW_SHOT_EXAMPLES = """
Q: How much money has each machine made?
SQL:
SELECT vm.id, vm.type, vm.address,
       ROUND(COALESCE(SUM(s.price_charged), 0), 2) AS total_revenue_dollars
FROM vending_machine AS vm
LEFT JOIN sale AS s ON s.vend_id = vm.id
GROUP BY vm.id, vm.type, vm.address;

Q: What is the profit on each product sold?
SQL:
SELECT mi.name,
       ROUND(SUM(s.price_charged - mi.price), 2) AS estimated_profit_dollars
FROM sale AS s
JOIN market_item AS mi ON mi.id = s.item_id
GROUP BY mi.id, mi.name;
"""

def get_schema_and_samples(conn):
    """Schema text (with foreign keys) plus 3 sample rows per table."""
    parts = []
    tables = conn.execute("SELECT name, sql FROM sqlite_master WHERE type='table'").fetchall()
    for name, create_sql in tables:
        parts.append(create_sql + ";")
        rows = conn.execute(f"SELECT * FROM {name} LIMIT 3").fetchall()
        parts.append(f"-- sample rows from {name}: {rows}")
    return "\n".join(parts)


def ask_gpt(system, user):
    resp = client.chat.completions.create(
        model=MODEL,
        temperature=0,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
    )
    return resp.choices[0].message.content.strip()


def question_to_sql(question, schema, strategy):
    system = (
        "You write SQLite queries. Given the database schema, reply with ONE SQL "
        "SELECT query and nothing else (no markdown, no explanation). "
        "Prices are stored in cents."
    )
    user = f"Schema:\n{schema}\n"
    if strategy == "few-shot":
        user += f"\nExamples:\n{FEW_SHOT_EXAMPLES}\n"
    user += f"\nQ: {question}\nSQL:"
    sql = ask_gpt(system, user)
    return sql.replace("```sql", "").replace("```", "").strip()


def run_sql(conn, sql):
    # Only allow reads
    if not sql.lstrip().lower().startswith("select"):
        raise ValueError("Refusing to run non-SELECT query")
    cur = conn.execute(sql)
    cols = [c[0] for c in cur.description]
    return cols, cur.fetchall()


def answer_in_english(question, sql, cols, rows):
    system = "You answer questions about a vending machine business in friendly plain English. Prices in the data are in cents; show dollars."
    user = f"Question: {question}\nSQL used: {sql}\nColumns: {cols}\nRows: {rows}\n\nAnswer the question."
    return ask_gpt(system, user)

def create_database():
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)

    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON")

    setup_path = os.path.join(BASE_DIR, "setup.sql")
    data_path = os.path.join(BASE_DIR, "setupData.sql")

    print("Creating tables from setup.sql...")
    with open(setup_path, encoding="utf-8") as file:
        conn.executescript(file.read())

    print("Tables created. Loading setupData.sql...")
    with open(data_path, encoding="utf-8") as file:
        data_sql = file.read()

    for number, statement in enumerate(data_sql.split(";"), start=1):
        if not statement.strip():
            continue

        try:
            conn.execute(statement)
        except sqlite3.IntegrityError:
            print(f"Foreign-key error in data statement {number}:")
            print(statement)
            print("Machine rows:", conn.execute(
                "SELECT * FROM vending_machine"
            ).fetchall())
            print("Lane rows:", conn.execute(
                "SELECT * FROM lane"
            ).fetchall())
            raise

    conn.commit()
    conn.execute("PRAGMA query_only = ON")
    return conn


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--strategy", choices=["zero-shot", "few-shot"], default="zero-shot")
    args = parser.parse_args()

    conn = create_database()
    schema = get_schema_and_samples(conn)
    print(f"Vending machine assistant ({args.strategy}). Type 'quit' to exit.")

    while True:
        question = input("\nAsk a question: ").strip()
        if question.lower() in ("quit", "exit", ""):
            break
        sql = question_to_sql(question, schema, args.strategy)
        print(f"\nSQL: {sql}")
        try:
            cols, rows = run_sql(conn, sql)
        except Exception as e:
            print(f"SQL failed: {e}")
            continue
        print(f"Rows: {rows}")
        print(f"\nAnswer: {answer_in_english(question, sql, cols, rows)}")


if __name__ == "__main__":
    main()