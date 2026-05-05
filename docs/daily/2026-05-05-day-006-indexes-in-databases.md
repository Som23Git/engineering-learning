# Day 006 — Indexes in Databases

Date: 2026-05-05

## Phase

Phase 1 — Backend Foundations

## Learning Objective

By the end of this lesson, you should understand why database indexes can make read queries much faster, and why indexes also add storage cost and slow down writes such as `INSERT`, `UPDATE`, and `DELETE`.

You should also be able to create a basic PostgreSQL index and compare query plans before and after using `EXPLAIN`.

## Why This Topic Matters

Indexes are one of the most important database performance tools in backend engineering.

In real systems, slow database queries often become a major bottleneck. An API may look simple, but behind it there may be a query scanning millions of rows. If that query runs on every request, the whole service can become slow or unstable.

Indexes help with:

- Faster lookups
- Faster filtering with `WHERE`
- Faster joins
- Faster sorting in some cases
- Lower database CPU usage for read-heavy workloads

But indexes are not free.

They also cause:

- More disk usage
- Slower writes
- More maintenance work for the database
- Possible bad performance if you add unnecessary indexes

As a backend or platform engineer, you need to understand indexes because production performance often depends on choosing the right ones.

## Simple Explanation

A database table is like a large list of records.

Imagine a `users` table:

```text
id | email              | name
---|--------------------|------
1  | alice@example.com  | Alice
2  | bob@example.com    | Bob
3  | carol@example.com  | Carol
...
```

If you ask:

```sql
SELECT * FROM users WHERE email = 'bob@example.com';
```

Without an index, the database may need to check every row until it finds the matching email.

That is called a table scan.

If the table has 100 rows, this is fine.

If the table has 100 million rows, this can be slow.

An index is a separate data structure that helps the database find rows faster. Instead of searching every row, the database can use the index to jump closer to the matching data.

But every time you insert or update data, the database also has to update the index. That is why indexes speed up reads but add write overhead.

## Real-World Analogy

Think about a book.

If you want to find every place where the word “database” appears, you have two options:

### Without an index

You read every page from the beginning until you find the word.

That works, but it is slow for a large book.

### With an index

You go to the back of the book, find “database”, and see the page numbers where it appears.

That is much faster.

But the book index has a cost:

- It takes extra pages.
- Someone has to build it.
- If the book changes, the index must be updated.

Database indexes work the same way.

They make searching faster, but they require extra storage and maintenance.

## Technical Explanation

In PostgreSQL, an index is a separate database object that stores selected column values in a structure optimized for lookup.

The most common index type is a B-tree index.

A B-tree index is useful for queries like:

```sql
WHERE email = 'alice@example.com'
WHERE created_at > '2026-01-01'
ORDER BY created_at
```

When you create an index, PostgreSQL can choose between different query strategies.

For example:

### Sequential scan

PostgreSQL reads the table row by row.

You may see this in `EXPLAIN` output as:

```text
Seq Scan
```

This can be fine for small tables or queries that return many rows.

### Index scan

PostgreSQL uses the index to find matching rows.

You may see this as:

```text
Index Scan
```

or sometimes:

```text
Bitmap Index Scan
```

This is often better when the query filters down to a small number of rows.

Important point: PostgreSQL does not always use an index just because one exists.

The query planner estimates the cost of different plans and chooses what it believes is cheapest. For small tables, PostgreSQL may still choose a sequential scan because scanning the whole table may be faster than using the index.

Indexes help most when:

- The table is large.
- The query filters on indexed columns.
- The query returns a small percentage of rows.
- The index matches the query pattern.

Indexes add overhead because for every write, PostgreSQL must update both:

1. The table data
2. The related indexes

For example, if a table has five indexes, an `INSERT` may need to update all five indexes.

That is why “index everything” is a bad strategy.

## Practical Example

Suppose we have a table storing users:

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email TEXT NOT NULL,
    name TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT now()
);
```

Insert test data:

```sql
INSERT INTO users (email, name)
SELECT
    'user' || generate_series || '@example.com',
    'User ' || generate_series
FROM generate_series(1, 100000);
```

Now search by email:

```sql
EXPLAIN SELECT * FROM users WHERE email = 'user50000@example.com';
```

You may see a plan like:

```text
Seq Scan on users
  Filter: (email = 'user50000@example.com'::text)
```

This means PostgreSQL is scanning the table and checking the `email` value row by row.

Now create an index:

```sql
CREATE INDEX idx_users_email ON users(email);
```

Run the query plan again:

```sql
EXPLAIN SELECT * FROM users WHERE email = 'user50000@example.com';
```

Now you may see something like:

```text
Index Scan using idx_users_email on users
  Index Cond: (email = 'user50000@example.com'::text)
```

This means PostgreSQL is using the index to find the matching row more directly.

The query should usually become faster because PostgreSQL no longer needs to scan every row.

However, after creating this index, every insert into `users` must also update `idx_users_email`.

For example:

```sql
INSERT INTO users (email, name)
VALUES ('newuser@example.com', 'New User');
```

PostgreSQL now writes to:

```text
users table
idx_users_email index
```

So reads by email are faster, but writes have slightly more work.

## Official Documentation To Read

- [PostgreSQL — Indexes](https://www.postgresql.org/docs/current/indexes.html)

## Good Reads

- [Use The Index, Luke](https://use-the-index-luke.com/)

## Where This Appears in Production

Indexes appear constantly in production systems.

Examples:

### User login

A login query often searches by email:

```sql
SELECT * FROM users WHERE email = $1;
```

You usually want an index on `email`.

### Fetching orders for a customer

```sql
SELECT * FROM orders WHERE customer_id = $1;
```

You usually want an index on `customer_id`.

### Finding recent events

```sql
SELECT * FROM events
WHERE created_at > now() - interval '1 hour';
```

An index on `created_at` may help, depending on the table size and query pattern.

### Joining tables

```sql
SELECT *
FROM orders
JOIN customers ON orders.customer_id = customers.id;
```

Indexes on join columns can make joins faster.

### Observability and logging systems

Large event tables often need indexes for fields like:

- `service_name`
- `timestamp`
- `trace_id`
- `user_id`
- `request_id`

Without indexes, dashboards and investigations can become painfully slow.

### Platform engineering

Internal developer platforms often store data about:

- deployments
- environments
- build jobs
- audit logs
- service ownership
- incidents

Indexes help these systems stay responsive as the data grows.

## Common Beginner Mistakes

### 1. Thinking indexes always make everything faster

Indexes usually help reads, but they can hurt writes.

Every index must be maintained when data changes.

### 2. Adding indexes without checking query plans

Do not guess blindly.

Use:

```sql
EXPLAIN
```

or, when appropriate:

```sql
EXPLAIN ANALYZE
```

`EXPLAIN` shows the planned query strategy.

`EXPLAIN ANALYZE` actually runs the query and shows real execution timing.

Be careful with `EXPLAIN ANALYZE` on write queries in production because it actually executes the statement.

### 3. Indexing columns that are not used in queries

If no important query filters, joins, or sorts by a column, indexing it may only waste space and slow writes.

### 4. Creating too many indexes

A table with many indexes can become expensive to write to.

This matters for high-write systems like:

- event ingestion
- metrics pipelines
- audit logs
- message processing tables
- job queues

### 5. Expecting indexes to help low-selectivity queries

An index helps most when it filters down to a small number of rows.

For example, indexing a `status` column with only three values may not always help:

```sql
status IN ('pending', 'active', 'disabled')
```

If many rows have the same status, PostgreSQL may choose a sequential scan.

### 6. Forgetting that indexes use storage

Indexes are stored on disk. Large tables with many indexes can use significant storage.

### 7. Not matching the index to the query

An index on `email` helps this:

```sql
WHERE email = 'a@example.com'
```

But it may not help this as much:

```sql
WHERE lower(email) = 'a@example.com'
```

The query expression matters.

## Related Concepts

- Query planner
- Sequential scan
- Index scan
- Bitmap index scan
- B-tree indexes
- Primary keys
- Unique indexes
- Foreign keys
- Query optimization
- Database normalization
- Write amplification
- Read-heavy workloads
- Write-heavy workloads
- Cardinality
- Selectivity
- `EXPLAIN`
- `EXPLAIN ANALYZE`

## Interview-Level Explanation

An index is a separate data structure that helps a database find rows faster without scanning the whole table. It improves read performance for queries that filter, join, or sort using indexed columns.

The tradeoff is that indexes require extra storage and must be updated on writes. So indexes can slow down `INSERT`, `UPDATE`, and `DELETE` operations. Good indexing means adding indexes that match important query patterns, not indexing every column.

## Hands-On Exercise

Use PostgreSQL to create an index and compare query plans before and after using `EXPLAIN`.

### Step 1: Open PostgreSQL

Use your local PostgreSQL setup from the previous lesson.

Open `psql`:

```bash
psql
```

Or connect to your database directly:

```bash
psql -d your_database_name
```

### Step 2: Create a test table

```sql
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email TEXT NOT NULL,
    name TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT now()
);
```

### Step 3: Insert test data

Insert 100,000 rows:

```sql
INSERT INTO users (email, name)
SELECT
    'user' || generate_series || '@example.com',
    'User ' || generate_series
FROM generate_series(1, 100000);
```

Check the row count:

```sql
SELECT COUNT(*) FROM users;
```

Expected result:

```text
100000
```

### Step 4: Run `EXPLAIN` before creating the index

```sql
EXPLAIN SELECT * FROM users WHERE email = 'user50000@example.com';
```

Look for something like:

```text
Seq Scan on users
```

This means PostgreSQL plans to scan the table.

### Step 5: Create an index on `email`

```sql
CREATE INDEX idx_users_email ON users(email);
```

### Step 6: Run `EXPLAIN` again

```sql
EXPLAIN SELECT * FROM users WHERE email = 'user50000@example.com';
```

Look for something like:

```text
Index Scan using idx_users_email on users
```

or:

```text
Bitmap Index Scan
```

This means PostgreSQL is using the index.

### Step 7: Compare with `EXPLAIN ANALYZE`

Now run:

```sql
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'user50000@example.com';
```

This actually executes the query and shows timing.

You can compare:

- Estimated cost
- Actual execution time
- Rows returned
- Scan type

### Step 8: Test a query that may not benefit much

Run:

```sql
EXPLAIN SELECT * FROM users;
```

This will likely use a sequential scan because you are asking for the whole table.

That is normal.

Indexes help when the database can avoid reading lots of unnecessary rows.

### Step 9: Observe index storage

Check table and index size:

```sql
SELECT
    pg_size_pretty(pg_relation_size('users')) AS table_size,
    pg_size_pretty(pg_indexes_size('users')) AS indexes_size;
```

This shows that indexes take additional storage.

### Step 10: Clean up if you want

```sql
DROP TABLE users;
```

## Expected Outcome

After this exercise, you should be able to explain:

- What an index is
- Why an index can make lookups faster
- How to create an index in PostgreSQL
- How to inspect a query plan with `EXPLAIN`
- What `Seq Scan` means
- What `Index Scan` means
- Why indexes require extra storage
- Why too many indexes can slow down writes
- Why PostgreSQL may not always use an index even if one exists

You should be able to say:

> An index helps PostgreSQL find matching rows faster by avoiding a full table scan. But the index must be stored and maintained, so it increases storage usage and adds overhead to writes.

## Quiz Questions

1. Why can an index make this query faster?

   ```sql
   SELECT * FROM users WHERE email = 'alice@example.com';
   ```

2. Why can too many indexes hurt write performance?

3. If PostgreSQL still uses a `Seq Scan` after you create an index, what are two possible reasons?

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

Next, learn about database constraints and relationships, especially primary keys, foreign keys, uniqueness, and how they protect data integrity in backend systems.
