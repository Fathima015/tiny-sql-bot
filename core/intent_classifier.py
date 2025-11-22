import re
import json
from typing import Optional, Dict, Any
from model.model_api import generate_candidates

# Valid schema tables (lowercase for comparisons)
SCHEMA_TABLES = ["users", "products", "orders"]
# Mapping to canonical capitalized names expected
CANONICAL = {"users": "Users", "products": "Products", "orders": "Orders"}


def parse_json_like(text: str) -> Optional[Dict[str, Any]]:
    """Try to extract and parse a JSON object from LLM output; mild fixes."""
    if not text:
        return None
    text = text.strip()
    m = re.search(r"(\{[\s\S]*?\})", text)
    if not m:
        return None

    chunk = m.group(1)
    chunk = chunk.replace("'", '"')
    chunk = re.sub(r",\s*}", "}", chunk)
    chunk = re.sub(r",\s*]", "]", chunk)

    try:
        return json.loads(chunk)
    except:
        return None


EXAMPLES = [
    {
        "q": "list all users",
        "json": {
            "tables": ["Users"], "joins": False,
            "filters": {}, "columns": ["*"],
            "group_by": [], "order_by": [], "limit": None
        }
    },
    {
        "q": "get email of Alice",
        "json": {
            "tables": ["Users"], "joins": False,
            "filters": {"name": "Alice"}, "columns": ["email"],
            "group_by": [], "order_by": [], "limit": None
        }
    },
    {
        "q": "show orders of Rahul",
        "json": {
            "tables": ["Orders", "Users"], "joins": True,
            "filters": {"name": "Rahul"}, "columns": ["o.*"],
            "group_by": [], "order_by": [], "limit": None
        }
    }
]


def build_intent_prompt(q: str) -> str:
    ex_text = ""
    for ex in EXAMPLES:
        ex_text += f"Q: {ex['q']}\nJSON: {json.dumps(ex['json'])}\n\n"

    return (
        "Return ONLY a JSON object with keys: "
        "{tables,joins,filters,columns,group_by,order_by,limit}\n"
        "Use only: Users, Products, Orders.\n"
        "Do NOT invent fields.\n\n" +
        ex_text +
        f"Q: {q}\nJSON:"
    )


def heuristic_from_question(question: str) -> Dict[str, Any]:
    q = question.lower()

    intent = {
        "tables": [],
        "joins": False,
        "filters": {},
        "columns": [],
        "group_by": [], "order_by": [], "limit": None
    }

    # table detection
    if "user" in q or "users" in q:
        intent["tables"].append("Users")
    if "product" in q:
        intent["tables"].append("Products")
    if "order" in q or "orders" in q:
        intent["tables"].append("Orders")

    # extract name (capitalized token)
    mname = re.search(r"\b([A-Z][a-z]{1,25})\b", question)
    if mname:
        name = mname.group(1)
        if name not in {"Users", "Products", "Orders"}:
            intent["filters"]["name"] = name
            if "Orders" in intent["tables"] and "Users" not in intent["tables"]:
                intent["tables"].append("Users")
                intent["joins"] = True

    # LIMIT
    mlim = re.search(r"(?:first|top|limit)\s+(\d+)", q)
    if mlim:
        intent["limit"] = int(mlim.group(1))

    # GROUP BY (simple)
    if "group" in q:
        intent["group_by"] = ["p.name"] if "product" in q else ["o.id"]

    # default columns
    if "Orders" in intent["tables"]:
        intent["columns"] = ["o.*"]
    elif intent["tables"]:
        intent["columns"] = ["*"]

    return intent


def explicit_table_check(question: str) -> Optional[str]:
    """Reject explicit fake tables after SQL verbs."""
    q = question.lower()
    matches = re.findall(r"(?:from|join|into|update|delete|insert|drop)\s+([a-zA-Z_]+)", q)
    for t in matches:
        if t not in SCHEMA_TABLES:
            return t
    return None


def classify_intent(question: str) -> Dict[str, Any]:
    prompt = build_intent_prompt(question)

    try:
        cands = generate_candidates(prompt, max_length=150, num_beams=6, num_return_sequences=3)
    except:
        cands = []

    parsed = None
    for c in cands:
        parsed = parse_json_like(c)
        if parsed:
            break

    if not parsed:
        parsed = heuristic_from_question(question)

    # defaults
    parsed.setdefault("tables", [])
    parsed.setdefault("joins", False)
    parsed.setdefault("filters", {})
    parsed.setdefault("columns", [])
    parsed.setdefault("group_by", [])
    parsed.setdefault("order_by", [])
    parsed.setdefault("limit", None)

    # normalize tables
    parsed["tables"] = [CANONICAL[t.lower()] for t in parsed["tables"] if t.lower() in CANONICAL]

    # strict mode: explicit SQL-verb table mention
    bad = explicit_table_check(question)
    if bad:
        parsed["tables"] = []
        parsed["filters"] = {}
        parsed["joins"] = False
        return parsed

    # default columns
    if not parsed["columns"]:
        if "Orders" in parsed["tables"]:
            parsed["columns"] = ["o.*"]
        elif parsed["tables"]:
            parsed["columns"] = ["*"]

    return parsed
