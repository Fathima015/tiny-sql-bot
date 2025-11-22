import re

FORBIDDEN = ["DROP", "DELETE", "ALTER", "TRUNCATE", "UPDATE", "INSERT"]

def check_forbidden(sql: str) -> bool:
    s = sql.upper()
    return any(f in s for f in FORBIDDEN)

def sql_valid(sql: str, conn):
    if not sql or "SELECT" not in sql.upper():
        return False, "Missing SELECT"

    try:
        conn.execute("EXPLAIN QUERY PLAN " + sql)
        return True, ""
    except Exception as e:
        return False, str(e)
