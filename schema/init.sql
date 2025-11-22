CREATE TABLE Users(
  id INTEGER PRIMARY KEY,
  name TEXT,
  email TEXT
);

CREATE TABLE Products(
  id INTEGER PRIMARY KEY,
  name TEXT,
  price REAL
);

CREATE TABLE Orders(
  id INTEGER PRIMARY KEY,
  user_id INTEGER,
  product_id INTEGER,
  quantity INTEGER,
  order_date TEXT,
  FOREIGN KEY(user_id) REFERENCES Users(id),
  FOREIGN KEY(product_id) REFERENCES Products(id)
);
