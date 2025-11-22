import sqlite3
from core.intent_classifier import classify_intent
from sql_builder import build_sql
from core.validator import sql_valid, check_forbidden

def generate_sql(question: str) -> str:
    conn = sqlite3.connect(":memory:")

    # Temporary fake schema so EXPLAIN works
    conn.executescript("""
        CREATE TABLE Users(id INT, name TEXT, email TEXT);
        CREATE TABLE Products(id INT, name TEXT, price REAL);
        CREATE TABLE Orders(id INT, user_id INT, product_id INT, quantity INT, order_date TEXT);
    """)

    # STEP 1: classify user intent
    intent = classify_intent(question)

    # STRICT-MODE: if classifier rejects everything
    if not intent.get("tables"):
        print("[ERROR] Unknown tables/words.")
        print("\n=== FULL LOG ===")
        print("[ATTEMPT 1] SQL:\n<none - strict mode blocked>\n")
        print("[ATTEMPT 2 - RETRY] SQL:\n<no retry due to strict mode>\n")
        return "/* failed to generate valid sql */"

    # STEP 2: build SQL from intent
    sql_1 = build_sql(intent)

    # STEP 3: forbidden keyword check
    if check_forbidden(sql_1):
        print("[ERROR] Forbidden keyword detected.")
        print("\n=== FULL LOG ===")
        print("[ATTEMPT 1] SQL:\n" + sql_1 + "\n")
        print("[ATTEMPT 2 - RETRY] SQL:\n<blocked because forbidden>\n")
        return "/* forbidden operation blocked */"

    # STEP 4: validate attempt 1
    valid1, err1 = sql_valid(sql_1, conn)

    if valid1:
        return sql_1

    # ATTEMPT 1 FAILED – go to RETRY
    print(f"[FAILURE] Attempt 1 failed: {err1}")

    # STEP 5: retry using a safe fallback SQL
    fallback_table = intent["tables"][0]
    retry_sql = f"SELECT * FROM {fallback_table} u;"
    valid2, err2 = sql_valid(retry_sql, conn)

    if valid2:
        print("[SUCCESS] Retry attempt passed validation.\n")
        return retry_sql

    print(f"[FAILURE] Retry attempt failed: {err2}")

    print("\n=== FULL LOG ===")
    print("[ATTEMPT 1] SQL:")
    print(sql_1, "\n")

    print("[ATTEMPT 2 - RETRY] SQL:")
    print(retry_sql, "\n")

    return "/* failed to generate valid sql */"
