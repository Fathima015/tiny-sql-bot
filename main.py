# main.py
from core.sql_generator import generate_sql

def main():
    print("SQL Generator is ready. Type your question.")
    print("Type 'quit' or 'exit' to stop.\n")
    while True:
        try:
            q = input("Enter your question: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting. Goodbye!")
            break
        if not q:
            continue
        if q.lower() in ("quit", "exit"):
            print("Exiting.")
            break
        sql = generate_sql(q)
        print("\nSQL OUTPUT:\n")
        print(sql)
        print("\n" + "-"*27 + "\n")

if __name__ == "__main__":
    main()
