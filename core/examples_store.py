import json, os

STORE = "core/fewshot_store.json"
DEFAULT = []

def load_store():
    if os.path.exists(STORE):
        with open(STORE, "r", encoding="utf-8") as f:
            return json.load(f)
    return DEFAULT

def save_example(q, sql):
    data = load_store()
    data.insert(0, {"q": q, "sql": sql})

    data = data[:30]
    with open(STORE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
