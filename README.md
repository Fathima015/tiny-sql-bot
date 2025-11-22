# Tiny SQL Bot (SLM Optimization Project)
## 1. Task Chosen
Option 3: The "Tiny" SQL Expert (SLM Optimization)

The objective of this task is to build a lightweight SQL Generator using a Small Language Model (<4B parameters) that can convert natural language into SQL, handle JOIN queries, and perform a validation + self-correction loop.

## 2. Project Overview
This project uses a small local model (HuggingFace FLAN-T5-base in offline mode) combined with deterministic Python logic to:

1.Parse natural language questions

2.Produce valid SQL

3.Enforce schema awareness

4.Detect forbidden operations

5.Self-correct when SQL is invalid

## 3. SQL Schema

A dummy relational schema with 3 related tables:

- ### Users
(id, name, email)
- ### Products
(id, name, price)
- ### Orders
(id, user_id, product_id, quantity, order_date)

This schema requires JOIN operations to answer queries such as
“show orders of Rahul” or
“list orders grouped by product name”.

# 4. Core Features

## 4.1 Small Model (<4B parameters)

Uses FLAN-T5-base locally.
All SQL shaping, safety rules, and fallback logic run on-device.

## 4.2 Schema Awareness

The classifier only accepts:
- Users
- Products
- Orders

Unknown tables or fields cause strict rejection.

## 4.3 Self-Correction Loop
Every query goes through:

### Step 1 — Generate SQL

From intent classifier + SQL builder.

### Step 2 — Validate

Check for:

Forbidden words (DROP, DELETE, TRUNCATE, UPDATE, INSERT)
SQL syntax validity using SQLite’s EXPLAIN QUERY PLAN

### Step 3 — Retry Logic

If Attempt 1 fails:
Retry with safer fallback SQL
Produce logs showing failure + success

# 5. How to Run the Project Locally
### Step 1 — Clone the repository

git clone https://github.com/<your-username>/tiny-sql-bot.git
cd tiny-sql-bot

### Step 2 — Create & activate a virtual environment

python -m venv venv
.\venv\Scripts\activate      (Windows)

### Step 3 — Install dependencies

pip install -r requirements.txt

### Step 4 — Run the main script
python main.py

You can now type English questions such as:

- show orders of Rahul
- list all products
- show first 3 users
- show orders grouped by product

# 6. Prompting Strategy

Two-layer approach:

## 6.1 Few-Shot Prompting

A minimal example-set primes the model to output structured JSON describing the query intent.

## 6.2 Rule-Based Reasoning

- After the model produces intent JSON:
- deterministic heuristics refine it
- strict mode removes invalid fields
- SQL builder converts it into correct SQL

This hybrid approach compensates for small model limitations.

# 7. Self-Correction Loop Evidence

The repository includes a “screenshots/” folder showing:

- Attempt 1 failing
- Attempt 2 succeeding
- Strict-mode blocks
- Working JOIN queries
- Forbidden keyword rejection

# 8. Why These Libraries/Models Were Used
## FLAN-T5-base

- Small enough for local CPU use
- Good at instruction following
- Easy to constrain with examples

## SQLite

Lightweight and perfect for validating generated SQL.

## Python + Deterministic Rules

Used for safety, schema-awareness, and reliability.
