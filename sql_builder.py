from typing import Dict, Any, List

ALLOWED = {
    "Users": ["id", "name", "email"],
    "Products": ["id", "name", "price"],
    "Orders": ["id", "user_id", "product_id", "quantity", "order_date"]
}

def quote(v):
    if isinstance(v, (int, float)):
        return str(v)
    s = str(v).replace("'", "''")
    return f"'{s}'"


def build_sql(intent: Dict[str, Any]) -> str:
    tables = intent.get("tables", [])
    joins = intent.get("joins", False)
    filters = intent.get("filters", {}) or {}
    columns = intent.get("columns", []) or []
    group_by = intent.get("group_by", []) or []
    order_by = intent.get("order_by", []) or []
    limit = intent.get("limit")

    if not tables:
        tables = ["Users"]

    alias = {}
    if "Orders" in tables:
        main = "Orders"; alias[main] = "o"
    else:
        main = tables[0]; alias[main] = "u" if main == "Users" else "p"

    # assign other aliases
    for t in tables:
        if t not in alias:
            alias[t] = t[0].lower()

    # SELECT
    sel = ", ".join(columns) if columns else "*"

    parts = [f"SELECT {sel}", f"FROM {main} {alias[main]}"]

    if joins:
        if "Orders" in tables and "Users" in tables:
            parts.append(f"JOIN Users u ON o.user_id = u.id")
        if "Orders" in tables and "Products" in tables:
            parts.append(f"JOIN Products p ON o.product_id = p.id")

    # WHERE
    where = []
    if "name" in filters and "Users" in tables:
        where.append(f"u.name = {quote(filters['name'])}")

    if where:
        parts.append("WHERE " + " AND ".join(where))

    if group_by:
        parts.append("GROUP BY " + ", ".join(group_by))

    if order_by:
        parts.append("ORDER BY " + ", ".join(order_by))

    if limit:
        parts.append(f"LIMIT {limit}")

    sql = "\n".join(parts)
    if not sql.endswith(";"):
        sql += ";"
    return sql
