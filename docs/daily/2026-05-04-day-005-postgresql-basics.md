# Day 005 — PostgreSQL Basics

Date: 2026-05-04

## Phase

Phase 1 — Backend Foundations

## Learning Objective

By the end of this lesson, you should understand the basics of relational databases using PostgreSQL.

You should be able to explain:

- What a relational database is
- What tables, rows, and columns are
- What a primary key is
- How to write basic SQL queries
- How to insert, read, and update data in a PostgreSQL table

## Why This Topic Matters

Most backend systems need to store data.

For example:

- User accounts
- Orders
- Payments
- Product catalogs
- Audit logs
- Permissions
- Application settings

PostgreSQL is one of the most widely used relational databases in production systems. As a backend or platform engineer, you will often work with PostgreSQL directly or indirectly through application code, migrations, dashboards, alerts, and production incidents.

Understanding PostgreSQL basics helps you:

- Design better data models
- Debug backend bugs involving stored data
- Write safer queries
- Understand application performance problems
- Communicate clearly with senior engineers and database administrators
- Avoid dangerous mistakes like updating or deleting the wrong records

## Simple Explanation

A database is a place where an application stores data.

A relational database stores data in tables.

A table is like a spreadsheet.

Example: a `users` table.

| id | name  | email             | active |
|----|-------|-------------------|--------|
| 1  | Alice | alice@example.com | true   |
| 2  | Bob   | bob@example.com   | true   |
| 3  | Cara  | cara@example.com  | false  |

In this table:

- The table name is `users`
- Each row is one user
- Each column is one piece of information about a user
- `id` is a unique identifier for each user
- SQL is the language used to create, read, update, and delete data

Common SQL operations:

```sql
-- Create a table
CREATE TABLE users (...);

-- Insert data
INSERT INTO users (...);

-- Read data
SELECT ... FROM users;

-- Update data
UPDATE users SET ... WHERE ...;

-- Delete data
DELETE FROM users WHERE ...;
```

The most important idea: databases are not just storage. They also enforce structure, rules, and relationships.

## Real-World Analogy

Think of PostgreSQL like a well-organized filing cabinet.

The database is the whole filing cabinet.

A table is one drawer, such as `users`, `orders`, or `payments`.

A row is one file inside the drawer.

A column is a field on the file, such as:

- Name
- Email
- Created date
- Status

A primary key is the unique file number. Even if two people have the same name, their file numbers are different.

SQL is how you ask the filing cabinet questions:

- “Show me all active users.”
- “Add this new user.”
- “Change Bob’s email address.”
- “Find the user with ID 42.”

## Technical Explanation

PostgreSQL is a relational database management system, often shortened to RDBMS.

A relational database organizes data into relations, commonly called tables.

### Table

A table defines the shape of stored data.

Example:

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

This creates a table named `users`.

### Column

A column defines one field of data.

Examples:

- `id`
- `name`
- `email`
- `active`
- `created_at`

Each column has a data type.

Examples:

- `TEXT`
- `INTEGER`
- `BOOLEAN`
- `TIMESTAMP`

### Row

A row is one record in the table.

Example:

```sql
INSERT INTO users (name, email)
VALUES ('Alice', 'alice@example.com');
```

This inserts one row into the `users` table.

### Primary Key

A primary key uniquely identifies each row.

In this example:

```sql
id SERIAL PRIMARY KEY
```

The `id` column is the primary key.

That means:

- Every row must have a unique `id`
- The `id` should not be reused for different users
- Other tables can refer to this `id`

### SQL

SQL stands for Structured Query Language.

It is used to interact with relational databases.

Common SQL commands include:

| Operation | SQL command |
|---|---|
| Create table | `CREATE TABLE` |
| Insert data | `INSERT INTO` |
| Read data | `SELECT` |
| Update data | `UPDATE` |
| Delete data | `DELETE` |

### `WHERE` Clause

The `WHERE` clause filters rows.

Example:

```sql
SELECT * FROM users
WHERE active = true;
```

This means:

“Show me all rows from the `users` table where `active` is true.”

The `WHERE` clause is especially important for updates and deletes.

Dangerous:

```sql
UPDATE users
SET active = false;
```

This updates every row in the table.

Safer:

```sql
UPDATE users
SET active = false
WHERE id = 2;
```

This updates only the user with `id = 2`.

## Practical Example

Here is a simple PostgreSQL example using a `users` table.

```sql
-- Create a users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Insert records
INSERT INTO users (name, email)
VALUES
    ('Alice', 'alice@example.com'),
    ('Bob', 'bob@example.com'),
    ('Cara', 'cara@example.com');

-- Query all users
SELECT * FROM users;

-- Query only active users
SELECT id, name, email
FROM users
WHERE active = true;

-- Update one row
UPDATE users
SET active = false
WHERE email = 'bob@example.com';

-- Confirm the update
SELECT id, name, email, active
FROM users
WHERE email = 'bob@example.com';
```

Expected result after the update:

| id | name | email           | active |
|----|------|-----------------|--------|
| 2  | Bob  | bob@example.com | false  |

The exact `id` value may differ depending on your database state.

## Official Documentation To Read

- [PostgreSQL — Tutorial](https://www.postgresql.org/docs/current/tutorial.html)
- [PostgreSQL — Getting Started](https://www.postgresql.org/docs/current/tutorial-start.html)

## Good Reads

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

## Where This Appears in Production

PostgreSQL appears in many real production systems.

Examples:

### User Management

A backend service may store users in a `users` table:

```text
users
- id
- email
- password_hash
- created_at
- last_login_at
```

### Orders and Payments

An e-commerce platform may store orders and payments:

```text
orders
- id
- user_id
- status
- total_amount
- created_at

payments
- id
- order_id
- provider
- status
- paid_at
```

### Application Configuration

Some systems store feature flags or app settings in PostgreSQL.

```text
feature_flags
- id
- name
- enabled
- updated_at
```

### Observability and Incident Debugging

During incidents, engineers often inspect database state.

Example questions:

- Did the user record exist?
- Was the payment marked as successful?
- Did a background job update the row?
- Are there duplicate records?
- Did an update affect too many rows?

### Platform Engineering

Platform engineers may manage:

- PostgreSQL backups
- Replication
- Database migrations
- Connection pooling
- Access control
- Monitoring and alerts
- Slow query investigation

Even if you are not a database administrator, you need enough PostgreSQL knowledge to operate backend systems safely.

## Common Beginner Mistakes

### 1. Forgetting the `WHERE` Clause

Dangerous:

```sql
UPDATE users
SET active = false;
```

This updates all users.

Better:

```sql
UPDATE users
SET active = false
WHERE id = 2;
```

Always check your `WHERE` clause before running `UPDATE` or `DELETE`.

### 2. Confusing Tables and Databases

A database contains tables.

Example:

```text
database: app_db

tables:
- users
- orders
- payments
```

The database is the container. Tables are inside it.

### 3. Thinking a Row and Column Are the Same Thing

A row is one record.

A column is one field.

In a `users` table:

```text
Row: Alice's full user record
Column: email
```

### 4. Not Using a Primary Key

Every important table should usually have a primary key.

Without a primary key, it becomes harder to:

- Identify one exact row
- Update a specific record
- Reference the row from another table
- Debug production data issues

### 5. Using Weak or Inconsistent Data Types

Example mistake:

```sql
active TEXT
```

Better:

```sql
active BOOLEAN
```

If a value is true/false, use `BOOLEAN`.

If a value is a timestamp, use `TIMESTAMP` or a related time type.

Data types help PostgreSQL protect the correctness of your data.

### 6. Using `SELECT *` Everywhere

`SELECT *` is useful while learning.

But in production code, it is often better to request only the columns you need.

Instead of:

```sql
SELECT * FROM users;
```

Prefer:

```sql
SELECT id, name, email FROM users;
```

This can reduce unnecessary data transfer and make code clearer.

### 7. Assuming Insert Order Is Query Order

Do not assume PostgreSQL returns rows in insertion order.

If order matters, use `ORDER BY`.

```sql
SELECT id, name, email
FROM users
ORDER BY id;
```

## Related Concepts

- SQL
- Relational databases
- Tables
- Rows
- Columns
- Primary keys
- Foreign keys
- Indexes
- Constraints
- Transactions
- Database migrations
- CRUD operations
- Connection strings
- Backups and restores
- Query performance
- Data modeling

## Interview-Level Explanation

PostgreSQL is a relational database system that stores structured data in tables. A table contains rows and columns, where each row represents one record and each column represents a field with a specific data type. A primary key uniquely identifies each row. SQL is used to create tables, insert records, query data, update rows, and delete data. In backend systems, PostgreSQL is commonly used to store durable application data such as users, orders, payments, and configuration.

## Hands-On Exercise

Use PostgreSQL to create a `users` table, insert records, query them, and update one row.

### Step 1: Start PostgreSQL

Use any local PostgreSQL setup you already have.

If PostgreSQL is installed locally, connect with:

```bash
psql
```

Depending on your setup, you may need to specify a user or database:

```bash
psql -U postgres
```

or:

```bash
psql -U postgres -d postgres
```

### Step 2: Create a Test Database

Inside `psql`, create a database:

```sql
CREATE DATABASE day005_demo;
```

Connect to it:

```sql
\c day005_demo
```

### Step 3: Create a `users` Table

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

Check that the table exists:

```sql
\dt
```

Inspect the table structure:

```sql
\d users
```

### Step 4: Insert Records

```sql
INSERT INTO users (name, email)
VALUES
    ('Alice', 'alice@example.com'),
    ('Bob', 'bob@example.com'),
    ('Cara', 'cara@example.com');
```

### Step 5: Query All Records

```sql
SELECT * FROM users;
```

You should see three rows.

### Step 6: Query Specific Columns

```sql
SELECT id, name, email
FROM users;
```

This returns only the selected columns.

### Step 7: Query With a Filter

```sql
SELECT id, name, email, active
FROM users
WHERE active = true;
```

This returns only active users.

### Step 8: Update One Row

Set Bob as inactive:

```sql
UPDATE users
SET active = false
WHERE email = 'bob@example.com';
```

### Step 9: Confirm the Update

```sql
SELECT id, name, email, active
FROM users
WHERE email = 'bob@example.com';
```

You should see Bob with:

```text
active = false
```

### Step 10: Practice Safe Updates

Before running an update, first run a `SELECT` with the same `WHERE` clause.

For example:

```sql
SELECT *
FROM users
WHERE email = 'bob@example.com';
```

Then run:

```sql
UPDATE users
SET active = false
WHERE email = 'bob@example.com';
```

This habit helps prevent accidental production mistakes.

### Step 11: Optional Cleanup

If you want to remove the test database, first connect to another database:

```sql
\c postgres
```

Then drop the demo database:

```sql
DROP DATABASE day005_demo;
```

## Expected Outcome

After completing this exercise, you should be able to:

- Explain what a relational database is
- Explain what a table is
- Explain the difference between rows and columns
- Create a PostgreSQL table
- Insert records into a table
- Query records using `SELECT`
- Filter records using `WHERE`
- Update one row using `UPDATE`
- Explain why primary keys are important
- Explain why `WHERE` is critical for safe updates and deletes

You should also be comfortable saying:

> PostgreSQL stores structured data in tables. Each table has columns that define the shape of the data, and rows that contain actual records. SQL is used to create, read, update, and delete data. A primary key uniquely identifies each row.

## Quiz Questions

1. What is the difference between a row and a column in a PostgreSQL table?

2. Why is a primary key important?

3. What could go wrong if you run this query without a `WHERE` clause?

```sql
UPDATE users
SET active = false;
```

## My Understanding

<!-- I will fill this manually after reading. -->

## Mistakes I Made

<!-- I will fill this manually after trying the exercise. -->

## Questions I Still Have

<!-- I will fill this manually. -->

## Learning Feedback

### Rating

<!-- 1 to 5 -->

### What was clear?

<!-- Fill after reading. -->

### What was confusing?

<!-- Fill after reading. -->

### What should be explained again?

<!-- Fill after reading. -->

### What style worked best?

<!-- Examples, analogy, diagrams, code, debugging story, etc. -->

### What should tomorrow include?

<!-- This will be read by the next automation run. -->

## What To Learn Next

Next, learn more SQL fundamentals: filtering, sorting, constraints, and relationships between tables.

A good next topic would be:

**SQL Basics — SELECT, WHERE, ORDER BY, INSERT, UPDATE, DELETE, and simple constraints.**
