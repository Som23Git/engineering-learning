# Day 010 — API Rate Limiting

Date: 2026-05-09

## Phase

Phase 1 — Backend Foundations

## Learning Objective

By the end of this lesson, you should understand how systems protect APIs from abuse and overload using rate limiting.

You should be able to explain:

- What API rate limiting is
- Why rate limits protect reliability
- The difference between fixed window, sliding window, and token bucket algorithms
- How to implement a simple in-memory token bucket rate limiter

## Why This Topic Matters

APIs are shared resources.

If one user, client, bot, bug, or attacker sends too many requests, they can overload your backend. That overload can affect everyone else using the system.

Rate limiting protects production systems by:

- Preventing accidental overload from buggy clients
- Reducing abuse from bots and attackers
- Protecting databases and downstream services
- Keeping service quality fair across users
- Helping APIs stay available during traffic spikes

In real backend and platform engineering, rate limiting is one of the basic controls used to keep systems reliable.

Authentication answers:

> “Who are you?”

Authorization answers:

> “What are you allowed to do?”

Rate limiting answers:

> “How often are you allowed to do it?”

## Simple Explanation

Rate limiting means putting a limit on how many requests someone can make in a period of time.

Example:

> A user can make 100 API requests per minute.

If the user sends 50 requests in a minute, everything is fine.

If the user sends 500 requests in a minute, the API starts rejecting requests.

Usually the API returns:

```http
HTTP/1.1 429 Too Many Requests
```

That means:

> “You are sending requests too quickly. Slow down.”

Rate limiting is not mainly about punishing users. It is about protecting the system so it stays healthy for everyone.

## Real-World Analogy

Imagine a coffee shop with one barista.

If customers enter normally, the barista can serve everyone.

But if one person walks in and orders 500 coffees at once, everyone else has to wait. The shop becomes unusable.

So the shop adds a rule:

> Each customer can order 5 drinks every 10 minutes.

This protects the barista, the queue, and the other customers.

An API works the same way.

The backend has limited capacity:

- CPU
- memory
- database connections
- network bandwidth
- external service limits

Rate limiting controls how quickly clients can consume that capacity.

## Technical Explanation

A rate limiter tracks request usage and decides whether to allow or reject each request.

A simplified flow looks like this:

```text
Client
  |
  v
Rate Limiter
  |
  |-- allowed --> API handler --> Database/service
  |
  |-- rejected --> 429 Too Many Requests
```

Rate limits are commonly applied by:

- IP address
- authenticated user ID
- API key
- organization/account ID
- route/path
- service/client identity

Examples:

```text
100 requests per minute per IP
1000 requests per hour per API key
10 login attempts per minute per user
5 expensive report exports per hour per organization
```

There are several common rate limiting algorithms.

### 1. Fixed Window

A fixed window counter divides time into fixed intervals.

Example:

```text
Limit: 100 requests per minute
Window: 12:00:00 to 12:00:59
```

If a user makes 100 requests during that minute, request 101 is rejected.

At the next minute, the counter resets.

```text
12:00:00 - 12:00:59 -> 100 allowed
12:01:00 - 12:01:59 -> counter resets
```

Advantages:

- Simple to implement
- Easy to understand
- Low storage cost

Problem:

Users can burst at the boundary.

Example:

```text
12:00:59 -> 100 requests
12:01:00 -> 100 more requests
```

That allows 200 requests in about 1 second, even though the limit says 100 per minute.

### 2. Sliding Window

A sliding window looks backward from the current time.

Example:

```text
Limit: 100 requests in the last 60 seconds
```

Instead of resetting at fixed minute boundaries, it checks the previous 60 seconds from now.

This is more accurate than fixed window.

Advantages:

- Reduces boundary bursts
- More fair than fixed window

Tradeoffs:

- More complex
- May require storing timestamps or approximate counters
- Can use more memory

### 3. Token Bucket

A token bucket uses a bucket that fills with tokens over time.

Each request costs one or more tokens.

If the bucket has enough tokens, the request is allowed.

If the bucket is empty, the request is rejected.

Example:

```text
Bucket capacity: 10 tokens
Refill rate: 1 token per second
Each request costs: 1 token
```

This means:

- The client can burst up to 10 requests immediately
- After that, they can continue at about 1 request per second
- If they stop sending traffic, the bucket refills

Token bucket is popular because it supports controlled bursts while still enforcing an average rate.

Example timeline:

```text
Start: bucket has 10 tokens

Client sends 10 requests quickly:
- all 10 allowed
- bucket now has 0 tokens

Client sends request 11 immediately:
- rejected

Wait 1 second:
- bucket refills 1 token

Client sends another request:
- allowed
```

### Why Rate Limits Protect Reliability

Without rate limits, one bad client can consume too many resources.

That can cause:

- Higher latency
- Database overload
- Thread pool exhaustion
- Queue buildup
- Memory pressure
- Increased cloud costs
- Outages for other users

Rate limiting creates a protective boundary before expensive work happens.

A good rate limiter should usually run before:

- Database queries
- expensive computations
- calls to third-party APIs
- background job creation
- authentication brute-force-sensitive operations

## Practical Example

Here is a simple in-memory token bucket rate limiter using Python.

This example is intentionally small and local. It is useful for learning, but it is not enough for multi-server production systems.

Create a file named:

```text
token_bucket.py
```

Add:

```python
import time
from dataclasses import dataclass


@dataclass
class TokenBucket:
    capacity: int
    refill_rate_per_second: float
    tokens: float
    last_refill_time: float

    def refill(self) -> None:
        now = time.time()
        elapsed = now - self.last_refill_time

        new_tokens = elapsed * self.refill_rate_per_second
        self.tokens = min(self.capacity, self.tokens + new_tokens)
        self.last_refill_time = now

    def allow_request(self, cost: int = 1) -> bool:
        self.refill()

        if self.tokens >= cost:
            self.tokens -= cost
            return True

        return False


class RateLimiter:
    def __init__(self, capacity: int, refill_rate_per_second: float):
        self.capacity = capacity
        self.refill_rate_per_second = refill_rate_per_second
        self.buckets = {}

    def allow_request(self, client_id: str) -> bool:
        if client_id not in self.buckets:
            self.buckets[client_id] = TokenBucket(
                capacity=self.capacity,
                refill_rate_per_second=self.refill_rate_per_second,
                tokens=self.capacity,
                last_refill_time=time.time(),
            )

        return self.buckets[client_id].allow_request()


if __name__ == "__main__":
    limiter = RateLimiter(
        capacity=5,
        refill_rate_per_second=1,
    )

    client = "user-123"

    print("Sending 10 requests quickly:")

    for i in range(10):
        allowed = limiter.allow_request(client)
        status = "allowed" if allowed else "rejected"
        print(f"request {i + 1}: {status}")

    print("\nWaiting 3 seconds for tokens to refill...\n")
    time.sleep(3)

    for i in range(5):
        allowed = limiter.allow_request(client)
        status = "allowed" if allowed else "rejected"
        print(f"request after wait {i + 1}: {status}")
```

Run it:

```bash
python token_bucket.py
```

Example output:

```text
Sending 10 requests quickly:
request 1: allowed
request 2: allowed
request 3: allowed
request 4: allowed
request 5: allowed
request 6: rejected
request 7: rejected
request 8: rejected
request 9: rejected
request 10: rejected

Waiting 3 seconds for tokens to refill...

request after wait 1: allowed
request after wait 2: allowed
request after wait 3: allowed
request after wait 4: rejected
request after wait 5: rejected
```

What happened?

```text
capacity = 5
refill_rate = 1 token per second
```

The first 5 requests were allowed because the bucket started full.

The next 5 requests were rejected because the bucket was empty.

After waiting 3 seconds, about 3 tokens were added back.

So about 3 more requests were allowed.

## Official Documentation To Read

- [NGINX — Rate limiting](https://docs.nginx.com/nginx/admin-guide/security-controls/controlling-access-proxied-http/)

## Good Reads

- [Cloudflare — What is rate limiting?](https://www.cloudflare.com/learning/bots/what-is-rate-limiting/)

## Where This Appears in Production

Rate limiting appears in many parts of production systems.

### API Gateways

API gateways often apply rate limits before traffic reaches backend services.

Example:

```text
Client -> API Gateway -> Backend Service
```

The gateway may enforce limits like:

```text
1000 requests per minute per API key
```

### Reverse Proxies

Reverse proxies such as NGINX can rate limit incoming HTTP requests before forwarding them to application servers.

Example:

```text
Internet -> NGINX -> Application
```

This is useful because bad traffic can be rejected before it consumes application resources.

### Authentication Systems

Login endpoints are commonly rate limited to reduce brute-force attacks.

Example:

```text
5 failed login attempts per minute per IP
```

or:

```text
10 login attempts per hour per account
```

### Public APIs

Public APIs usually rate limit by API key, user, or organization.

Example:

```text
Free plan: 1000 requests per day
Paid plan: 100000 requests per day
```

### Expensive Endpoints

Some endpoints are more expensive than others.

Examples:

- report generation
- search queries
- file exports
- image processing
- AI model requests
- payment operations

These may need stricter rate limits than simple read endpoints.

### Internal Platform Systems

Internal systems also use rate limiting.

Example:

```text
Service A -> Service B
```

If Service A has a bug and loops infinitely, it could overload Service B.

Internal rate limits help contain the blast radius.

## Common Beginner Mistakes

### 1. Thinking Rate Limiting Is Only for Security

Rate limiting helps security, but it is also a reliability tool.

It protects the system from:

- accidental client bugs
- traffic spikes
- overloaded dependencies
- expensive operations
- noisy neighbors

### 2. Only Rate Limiting by IP Address

IP-based limits are useful, but they are not always enough.

Problems:

- Many users may share one IP address
- One user may use many IP addresses
- Mobile networks and corporate networks often use shared IPs
- Attackers may rotate IPs

For authenticated APIs, rate limiting by user ID, organization ID, or API key is often better.

### 3. Forgetting Distributed Systems

An in-memory limiter works only inside one process.

If you run 5 application servers, each server has its own memory.

That means this limit:

```text
100 requests per minute
```

could accidentally become:

```text
500 requests per minute
```

if each server independently allows 100 requests.

Production systems often use a shared store or centralized layer, such as:

- API gateway
- reverse proxy
- Redis-backed rate limiter
- service mesh
- load balancer-level enforcement

### 4. Setting Limits Without Understanding Traffic

Limits should be based on real usage patterns.

Bad limits can:

- block legitimate users
- fail to stop abusive users
- create confusing customer issues
- hide capacity problems

Use metrics before and after adding rate limits.

### 5. Not Returning Useful Error Responses

A good rate-limited response should use:

```http
429 Too Many Requests
```

It may also include helpful headers such as retry information.

Example:

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 30
```

This tells the client to retry after 30 seconds.

### 6. Applying One Limit to Everything

Not all endpoints have the same cost.

This endpoint may be cheap:

```http
GET /health
```

This endpoint may be expensive:

```http
POST /reports/monthly-export
```

Expensive endpoints often need stricter limits.

### 7. Confusing Rate Limiting With Quotas

Rate limiting controls request speed.

Example:

```text
100 requests per minute
```

Quotas control total usage over a larger period.

Example:

```text
1 million requests per month
```

They are related, but not the same.

## Related Concepts

- API gateways
- Reverse proxies
- Load balancers
- NGINX
- HTTP 429 Too Many Requests
- Retry-After header
- Authentication
- Authorization
- API keys
- Abuse prevention
- DDoS protection
- Backpressure
- Circuit breakers
- Throttling
- Quotas
- Redis
- Distributed locks and counters
- Observability
- SLOs and error budgets
- Multi-tenant systems
- Noisy neighbor problem

## Interview-Level Explanation

API rate limiting controls how many requests a client can make in a given time period. It protects backend reliability by preventing one user, bot, bug, or service from consuming too much capacity.

Common algorithms include fixed window, sliding window, and token bucket.

Fixed window is simple but can allow bursts at window boundaries. Sliding window is more accurate because it checks usage over the most recent time period. Token bucket allows short bursts while enforcing a steady average rate by refilling tokens over time.

In production, rate limits are often enforced at an API gateway, reverse proxy, or shared distributed store so limits work across multiple servers.

## Hands-On Exercise

Implement a simple in-memory token bucket rate limiter.

### Goal

Build a small program that decides whether a request should be allowed or rejected.

### Requirements

Your limiter should support:

- a bucket capacity
- a refill rate
- one bucket per client ID
- allowing a request when tokens are available
- rejecting a request when tokens are not available

### Step 1: Create the File

Create:

```bash
touch token_bucket.py
```

### Step 2: Define the Token Bucket

Create a `TokenBucket` object with:

```text
capacity
refill_rate_per_second
tokens
last_refill_time
```

The bucket should refill based on elapsed time.

### Step 3: Implement Request Checking

Add a method like:

```python
allow_request()
```

It should:

1. Refill tokens based on time passed
2. Check whether at least 1 token is available
3. Subtract 1 token if allowed
4. Return `True` for allowed
5. Return `False` for rejected

### Step 4: Support Multiple Clients

Create a `RateLimiter` class that stores buckets in a dictionary:

```python
self.buckets = {}
```

Use `client_id` as the key.

Example:

```python
limiter.allow_request("user-123")
limiter.allow_request("user-456")
```

Each client should have an independent bucket.

### Step 5: Test Burst Behavior

Use:

```text
capacity = 5
refill_rate_per_second = 1
```

Send 10 requests immediately.

Expected behavior:

```text
First 5: allowed
Next 5: rejected
```

### Step 6: Test Refill Behavior

Wait 3 seconds.

Then send more requests.

Expected behavior:

```text
About 3 requests should be allowed
Then requests should be rejected again
```

### Step 7: Add Logging

Print output like:

```text
client=user-123 request=1 result=allowed
client=user-123 request=2 result=allowed
client=user-123 request=6 result=rejected
```

### Step 8: Think About Production Limits

Write short answers to these questions:

1. Why is this in-memory limiter not enough if the app runs on multiple servers?
2. What key would you rate limit by: IP, user ID, API key, or organization ID?
3. Which endpoints in a real API should have stricter rate limits?

## Expected Outcome

After completing the exercise, you should be able to:

- Explain what rate limiting is
- Explain why rate limiting protects API reliability
- Describe fixed window rate limiting
- Describe sliding window rate limiting
- Describe token bucket rate limiting
- Implement a simple in-memory token bucket limiter
- Explain why in-memory rate limiting has limitations in distributed production systems
- Recognize when to return `429 Too Many Requests`

## Quiz Questions

1. What problem can happen with fixed window rate limiting at the boundary between two windows?

2. Why does token bucket allow short bursts while still enforcing an average request rate?

3. Why is an in-memory rate limiter unsafe as the only rate limiter when your application runs on multiple servers?

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

Next, learn about API timeouts, retries, and backoff.

Rate limiting protects your service from receiving too much traffic. Timeouts and retries control what happens when services are slow, unavailable, or failing. Together, they are core API reliability patterns.
