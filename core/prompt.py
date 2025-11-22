SCHEMA = """
Users(id, name, email)
Products(id, name, price)
Orders(id, user_id, product_id, quantity, order_date)
"""

EXAMPLES = """
Q: list all users
SQL: SELECT * FROM Users;

Q: list all products
SQL: SELECT * FROM Products;

Q: get email of Alice
SQL: SELECT email FROM Users WHERE name = 'Alice';

Q: show orders of Alice
SQL: SELECT o.* FROM Orders o
    JOIN Users u ON o.user_id = u.id
    WHERE u.name = 'Alice';

Q: show orders with user names
SQL: SELECT o.*, u.name FROM Orders o
    JOIN Users u ON o.user_id = u.id;

Q: show products in orders
SQL: SELECT o.*, p.name FROM Orders o
    JOIN Products p ON o.product_id = p.id;
"""

RULES = """
Generate ONLY valid SQL.
Follow the schema exactly.
Use correct column names.
Use JOINs exactly as shown.
Use aliases o, u, p only.
Never invent columns or tables.
Never explain anything.
Always end with a semicolon.
"""

def build_prompt(question):
    return (
        f"{RULES}\n"
        f"Schema:\n{SCHEMA}\n"
        f"{EXAMPLES}\n"
        f"Q: {question}\nSQL:"
    )
