import sqlite3

conn=sqlite3.connect("database.db")
cursor=conn.cursor()

with open("schema/init.sql","r") as f:
    cursor.executescript(f.read())

cursor.execute("INSERT INTO Users(name, email) VALUES ('Alice', 'alice@mail.com')")
cursor.execute("INSERT INTO Users(name, email) VALUES ('Rahul', 'rahul@mail.com')")

cursor.execute("INSERT INTO Products(name, price) VALUES ('Laptop', 90000)")
cursor.execute("INSERT INTO Products(name, price) VALUES ('Mouse', 800)")

cursor.execute("""
INSERT INTO Orders(user_id, product_id, quantity, order_date)
VALUES (1, 1, 1, '2024-03-10')
""")

cursor.execute("""
INSERT INTO Orders(user_id, product_id, quantity, order_date)
VALUES (2, 2, 3, '2024-03-12')
""")

conn.commit()
conn.close()

print("Database created and sample data added.")