# Day 007 — Redis as a Cache

Date: 2026-05-06

## Phase

Phase 1 — Backend Foundations

## Learning Objective

By the end of this lesson, you should understand how Redis can be used as a cache to reduce database load and improve application latency.

You should be able to explain:

- What Redis is commonly used for
- What a cache hit is
- What a cache miss is
- What TTL means
- Why cached data must expire or be invalidated
- Why caching improves performance but also adds complexity

## Why This Topic Matters

Most backend systems eventually hit the same problem:

> Reading from the database for every request becomes too slow or too expensive.

Databases are powerful, but they are not free. Every database query consumes CPU, memory, disk I/O, locks, connections, and network time.

Redis is often used as a fast in-memory cache in front of a database.

In production, Redis is commonly used to:

- Reduce database read load
- Improve API response latency
- Store temporary values
- Cache expensive computations
- Cache sessions or authentication-related data
- Rate-limit users or APIs
- Store short-lived distributed coordination data

Caching is one of the most common backend performance techniques, but it is also one of the easiest to misuse.

A bad cache can return stale data, hide bugs, increase operational complexity, or make production debugging harder.

## Simple Explanation

Redis is a very fast key-value store.

You store data using a key:

```text
user:123
```

And Redis stores a value for that key:

```json
{"id":123,"name":"Asha"}
```

Instead of asking the database every time:

```text
Application -> Database
```

The application first checks Redis:

```text
Application -> Redis
```

If Redis has the data, the application can return it quickly.

If Redis does not have the data, the application asks the database, then stores the result in Redis for next time.

This pattern helps avoid repeated database work.

## Real-World Analogy

Imagine you are studying from a large textbook.

The textbook is like your database. It has the full truth, but looking things up takes time.

Now imagine you keep a small sticky note on your desk with facts you use often.

The sticky note is like Redis.

When you need an answer:

1. First, you check the sticky note.
2. If the answer is there, you get it quickly.
3. If it is not there, you open the textbook.
4. After finding the answer, you may write it on the sticky note for next time.

But there is a problem:

What if the textbook gets updated and your sticky note is now wrong?

That is the hard part of caching.

Caching is fast, but keeping cached data correct is difficult.

## Technical Explanation

Redis is an in-memory data store commonly used as a cache.

“In-memory” means Redis primarily stores data in RAM, which is much faster than disk-based storage. This makes Redis very fast for simple reads and writes.

A basic cache flow looks like this:

```text
Client
  |
  v
Backend API
  |
  v
Check Redis cache
  |
  |-- cache hit  --> return cached data
  |
  |-- cache miss --> query database
                    store result in Redis
                    return data
```

### Cache Hit

A cache hit means the requested data exists in Redis.

Example:

```text
GET user:123
```

Redis returns a value.

The application does not need to query the database.

### Cache Miss

A cache miss means Redis does not have the requested data.

Example:

```text
GET user:123
```

Redis returns:

```text
(nil)
```

The application then queries the database and may store the result in Redis.

### TTL

TTL means “time to live.”

It controls how long a key should exist before Redis automatically deletes it.

Example:

```text
EXPIRE user:123 60
```

This means:

> Delete `user:123` after 60 seconds.

TTL helps prevent Redis from serving old data forever.

### Invalidation

Invalidation means removing or updating cached data when the real data changes.

Example:

A user updates their profile name.

The database now has:

```json
{"id":123,"name":"New Name"}
```

But Redis may still have:

```json
{"id":123,"name":"Old Name"}
```

To avoid returning stale data, the application should delete or update the cache:

```text
DEL user:123
```

The next request will miss the cache, fetch fresh data from the database, and repopulate Redis.

### Why Caching Is Hard

Caching sounds simple:

> Put data in Redis. Read it later.

But in production, difficult questions appear:

- How long should data stay cached?
- What happens if the database updates but Redis still has old data?
- What happens if Redis is down?
- What happens when many requests miss the cache at the same time?
- Should every endpoint be cached?
- How much memory should Redis use?
- What should happen when Redis runs out of memory?
- Is slightly stale data acceptable?

Caching is a tradeoff between speed, correctness, cost, and complexity.

## Practical Example

Imagine an API endpoint:

```text
GET /users/123
```

Without Redis:

```text
Client -> API -> Database -> API -> Client
```

Every request hits the database.

With Redis:

```text
Client -> API -> Redis
              |
              |-- hit  --> return user
              |
              |-- miss --> Database
                           store in Redis
                           return user
```

Example cache-aside logic:

```js
async function getUser(userId) {
  const cacheKey = `user:${userId}`;

  // 1. Try Redis first
  const cachedUser = await redis.get(cacheKey);

  if (cachedUser) {
    console.log("cache hit");
    return JSON.parse(cachedUser);
  }

  console.log("cache miss");

  // 2. Query database if not in cache
  const user = await database.users.findById(userId);

  if (!user) {
    return null;
  }

  // 3. Store result in Redis with TTL
  await redis.set(cacheKey, JSON.stringify(user));
  await redis.expire(cacheKey, 60);

  return user;
}
```

This is called the **cache-aside pattern**.

The application is responsible for:

1. Checking the cache
2. Loading from the database on miss
3. Writing back to the cache
4. Expiring or invalidating cached data

A more compact version in Redis can use `SET` with expiration options, but for this lesson we focus on the beginner commands:

- `SET`
- `GET`
- `EXPIRE`
- `DEL`

## Official Documentation To Read

- [Redis — Docs](https://redis.io/docs/latest/)
- [Redis — Quick starts](https://redis.io/docs/latest/develop/get-started/)

## Good Reads

- [Redis — Get started with Redis Open Source](https://redis.io/docs/latest/get-started/)

## Where This Appears in Production

Redis caching appears in many real backend systems.

Common examples:

### User Profile Cache

Instead of querying the database every time a user profile is displayed, the service caches user data:

```text
user:123 -> {"id":123,"name":"Asha"}
```

### Product Catalog Cache

E-commerce systems often cache product pages, prices, categories, or inventory-related reads.

```text
product:987 -> {"id":987,"name":"Keyboard","price":59.99}
```

### Authentication and Session Data

Redis is often used for short-lived session tokens or login state.

```text
session:abc123 -> {"userId":123,"expiresAt":"..."}
```

### Rate Limiting

APIs may use Redis to count requests per user or IP address.

```text
rate_limit:user:123 -> 42
```

### Expensive Computation Results

If a report takes 5 seconds to calculate, the result may be cached for a few minutes.

```text
report:daily-sales:2026-05-06 -> {...}
```

### Platform Engineering Use Cases

Platform teams may use Redis-backed services for:

- Shared cache layers
- Feature flag state
- API gateway rate limits
- Job queues or temporary work coordination
- Short-lived service metadata

Redis is common because it is fast, simple, and widely supported.

## Common Beginner Mistakes

### 1. Thinking Redis Replaces the Database

Redis is usually not the source of truth for business data.

The database is still the durable source of truth.

Redis is commonly a fast temporary copy.

### 2. Caching Without a TTL

If you cache data without expiration, stale data may live forever.

Bad:

```text
SET user:123 '{"id":123,"name":"Old Name"}'
```

Better:

```text
SET user:123 '{"id":123,"name":"Asha"}'
EXPIRE user:123 60
```

### 3. Forgetting Invalidation

If the database changes, the cached copy may become wrong.

When data changes, you usually need to:

- Delete the cache key
- Update the cache key
- Use a short TTL
- Or combine these strategies

### 4. Caching Everything

Not all data should be cached.

Good candidates:

- Frequently read data
- Expensive database queries
- Data that can tolerate slight staleness
- Data shared by many users

Bad candidates:

- Rarely used data
- Highly sensitive data without careful controls
- Data that must be immediately consistent
- Data that changes constantly

### 5. Not Handling Redis Failures

Redis can go down.

Your application should not always completely fail just because the cache is unavailable.

In many systems, the safer behavior is:

```text
If Redis fails, query the database directly.
```

This is called graceful degradation.

### 6. Using Vague Key Names

Bad key:

```text
123
```

Better key:

```text
user:123
```

Even better when needed:

```text
prod:user:123
```

Clear key names help debugging and avoid collisions.

### 7. Not Thinking About Stale Data

Cached data can be old.

Sometimes that is acceptable.

Sometimes it is dangerous.

Example where stale data may be acceptable:

```text
Homepage trending posts
```

Example where stale data may be dangerous:

```text
Bank account balance
```

## Related Concepts

- Key-value stores
- Cache-aside pattern
- Cache hit
- Cache miss
- TTL
- Expiration
- Invalidation
- Stale data
- Database read load
- Latency
- Hot keys
- Graceful degradation
- Distributed systems consistency
- Source of truth
- Observability for cache performance

## Interview-Level Explanation

Redis is often used as an in-memory cache in front of a database to reduce read load and improve latency. The application checks Redis first. If the data exists, that is a cache hit and the app returns it quickly. If it does not exist, that is a cache miss, so the app queries the database and stores the result in Redis for future requests. Cached data usually has a TTL so it expires automatically. When underlying data changes, the cache may need to be invalidated or updated. Caching improves performance, but it adds complexity because stale data, cache failures, memory limits, and invalidation bugs must be handled carefully.

## Hands-On Exercise

Use Redis `SET`, `GET`, `EXPIRE`, and `DEL` commands from `redis-cli`.

### Step 1: Start Redis

If Redis is already installed and running, open a terminal and connect:

```bash
redis-cli
```

You should see a prompt like:

```text
127.0.0.1:6379>
```

Test the connection:

```redis
PING
```

Expected response:

```text
PONG
```

### Step 2: Store a Value with `SET`

Set a fake user profile in Redis:

```redis
SET user:123 '{"id":123,"name":"Asha","role":"admin"}'
```

Expected response:

```text
OK
```

You have now stored a value using the key:

```text
user:123
```

### Step 3: Read the Value with `GET`

Read the cached value:

```redis
GET user:123
```

Expected response:

```json
"{\"id\":123,\"name\":\"Asha\",\"role\":\"admin\"}"
```

This is a cache hit because Redis has the key.

### Step 4: Try a Missing Key

Run:

```redis
GET user:999
```

Expected response:

```text
(nil)
```

This is a cache miss because Redis does not have that key.

In a real backend, the application would now query the database.

### Step 5: Add a TTL with `EXPIRE`

Set an expiration time of 30 seconds:

```redis
EXPIRE user:123 30
```

Expected response:

```text
(integer) 1
```

This means Redis accepted the expiration.

Optional: check the TTL:

```redis
TTL user:123
```

You should see a number counting down:

```text
(integer) 24
```

### Step 6: Wait for the Key to Expire

Wait about 30 seconds.

Then run:

```redis
GET user:123
```

Expected response:

```text
(nil)
```

Redis automatically deleted the key after the TTL expired.

This is now a cache miss.

### Step 7: Recreate the Key

Set the user again:

```redis
SET user:123 '{"id":123,"name":"Asha","role":"admin"}'
```

Read it:

```redis
GET user:123
```

Expected result: the user data should be returned again.

### Step 8: Delete the Key with `DEL`

Now simulate cache invalidation.

Imagine the user changed their profile in the database. You want to remove the old cached copy.

Run:

```redis
DEL user:123
```

Expected response:

```text
(integer) 1
```

Now try to read it:

```redis
GET user:123
```

Expected response:

```text
(nil)
```

The cache entry was manually invalidated.

### Step 9: Think Through the Backend Flow

Write down what your API would do for this request:

```text
GET /users/123
```

Use this flow:

```text
1. Check Redis key user:123
2. If found, return cached value
3. If not found, query database
4. Store database result in Redis
5. Set TTL
6. Return response
```

### Step 10: Practice Explaining the Four Terms

In your own words, explain:

```text
Cache hit:
Cache miss:
TTL:
Invalidation:
```

Keep each answer to one or two sentences.

## Expected Outcome

After this exercise, you should be able to:

- Use `redis-cli` to store a value with `SET`
- Retrieve a value with `GET`
- Add expiration using `EXPIRE`
- Delete cached data with `DEL`
- Explain what a cache hit is
- Explain what a cache miss is
- Explain what TTL means
- Explain why invalidation is needed
- Explain why caching is useful but difficult

You should also understand this important production tradeoff:

> Redis can make reads much faster, but your application must handle stale data, expiration, invalidation, and Redis failures carefully.

## Quiz Questions

1. What is the difference between a cache hit and a cache miss?

2. Why should cached data usually have a TTL?

3. If a user updates their profile in the database, why might you need to delete or update the Redis cache key?

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

Next, learn the **cache-aside pattern in a real backend API**.

You already practiced Redis commands manually. The next logical step is to connect Redis to an application and implement this full flow:

```text
API request
  -> check Redis
  -> on miss, query database
  -> store result with TTL
  -> return response
```

This will connect caching to real backend application design.
