import re

def clean_sql(text: str) -> str:
    """
    Extract a clean SQL query from messy LLM output.
    Takes the first SELECT block (even if missing semicolon) and appends semicolon.
    """
    if not text:
        return ""

    text = text.replace("```sql", "").replace("```", "").replace("SQL:", "").strip()

    match = re.search(r"(SELECT[\s\S]*)", text, re.IGNORECASE)
    if match:
        sql = match.group(1).strip()

        if ";" in sql:
            sql = sql.split(";")[0] + ";"
        else:
            sql = sql.rstrip() + ";"

        sql = re.sub(r"(SELECT\s+)+SELECT", "SELECT", sql, flags=re.IGNORECASE)
        sql = re.sub(r"(FROM\s+)+FROM", "FROM", sql, flags=re.IGNORECASE)

        return sql.strip()

    lines = text.splitlines()
    for line in lines:
        if "SELECT" in line.upper():
            line = line.strip()
            if ";" not in line:
                line = line + ";"
            return line

    return ""
