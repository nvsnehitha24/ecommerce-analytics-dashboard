"""
Runs all SQL queries in queries.sql against the real ecommerce.db,
prints results to the console, and writes ANALYSIS.md with the
real computed numbers filled in.

Usage:
    python run_analysis.py "C:\\path\\to\\your\\ecommerce.db"

If no path is given, it defaults to ./data/ecommerce.db (relative
to wherever you run this script from).
"""

import sqlite3
import sys
import re

DB_PATH = sys.argv[1] if len(sys.argv) > 1 else "data/ecommerce.db"

def run_query(conn, query):
    cur = conn.cursor()
    cur.execute(query)
    cols = [d[0] for d in cur.description]
    rows = cur.fetchall()
    return cols, rows

def print_table(cols, rows, limit=15):
    print(" | ".join(cols))
    print("-" * 60)
    for r in rows[:limit]:
        print(" | ".join(str(x) for x in r))
    if len(rows) > limit:
        print(f"... ({len(rows) - limit} more rows)")
    print()

def main():
    conn = sqlite3.connect(DB_PATH)
    sql_text = open("queries.sql", encoding="utf-8").read()

    # Split on the numbered section headers to isolate each query block
    blocks = re.split(r"-- \d\. ", sql_text)[1:]  # drop preamble
    titles = re.findall(r"-- \d\. (.+)", sql_text)

    results = {}
    for title, block in zip(titles, blocks):
        # strip trailing comment lines and grab the actual SQL
        query = block.split("\n", 1)[1] if "\n" in block else block
        # remove any leftover comment lines within the block
        query_lines = [l for l in query.split("\n") if not l.strip().startswith("--")]
        query = "\n".join(query_lines).strip()
        if not query:
            continue
        print(f"\n===== {title} =====")
        try:
            cols, rows = run_query(conn, query)
            print_table(cols, rows)
            results[title] = (cols, rows)
        except Exception as e:
            print(f"ERROR running this query: {e}")

    conn.close()

    # ---- Build ANALYSIS.md from whatever we got ----
    md = ["# SQL Analysis Notes — E-Commerce Customer & Revenue Analysis\n"]
    md.append("Findings below are computed directly from `ecommerce.db` "
               "by running `queries.sql` via `run_analysis.py`.\n")

    for title, (cols, rows) in results.items():
        md.append(f"## {title}\n")
        md.append("| " + " | ".join(cols) + " |")
        md.append("|" + "---|" * len(cols))
        for r in rows[:20]:
            md.append("| " + " | ".join(str(x) for x in r) + " |")
        md.append("")

    with open("ANALYSIS.md", "w", encoding="utf-8") as f:
        f.write("\n".join(md))

    print("\nWrote ANALYSIS.md with real results.")

if __name__ == "__main__":
    main()
