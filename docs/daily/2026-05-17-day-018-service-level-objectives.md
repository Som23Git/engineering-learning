# Day 018 — Service Level Objectives

Date: 2026-05-17

## Phase

Phase 3 — Reliability and Observability

## Learning Objective

By the end of this lesson, you should understand how engineering teams define reliability targets using:

- **SLIs** — Service Level Indicators
- **SLOs** — Service Level Objectives
- **SLAs** — Service Level Agreements
- **Error budgets**

You should also understand why most production systems should **not** aim for 100% reliability.

## Why This Topic Matters

In real backend and platform engineering, reliability is not just “keep the service up.”

Teams need a clear way to answer questions like:

- Is the API reliable enough?
- Are users actually having a good experience?
- Should we ship new features or pause to fix reliability issues?
- How much failure is acceptable?
- When should an alert wake someone up?

Without SLOs, reliability discussions become emotional and vague:

> “The service feels slow.”  
> “Users are complaining.”  
> “We need five nines.”  
> “Everything must be perfect.”

SLOs make reliability measurable.

They help teams make better tradeoffs between:

- Speed of development
- System stability
- Infrastructure cost
- User experience
- Operational burden

In production engineering, SLOs are one of the most important tools for deciding whether a system is healthy enough.

## Simple Explanation

An **SLI** is a measurement.

An **SLO** is a target for that measurement.

An **SLA** is a promise, usually written in a contract.

An **error budget** is how much unreliability you are allowed to have before you need to slow down and fix the system.

Example:

```text
SLI:
The percentage of successful HTTP requests to /api/orders.

SLO:
99.9% of /api/orders requests should succeed over 30 days.

Error budget:
0.1% of requests are allowed to fail during that 30-day window.
```

If your system receives 1,000,000 requests in 30 days and your SLO is 99.9%, then:

```text
Allowed successful requests: 999,000
Allowed failed requests:     1,000
```

Those 1,000 allowed failures are your **error budget**.

If you use up the budget too quickly, the team should focus on reliability instead of shipping risky changes.

## Real-World Analogy

Imagine a delivery company.

They do not promise:

> “Every package will arrive perfectly on time forever.”

That would be unrealistic and expensive.

Instead, they might say:

> “99% of packages will arrive within 2 business days.”

Here is how the reliability concepts map:

| Reliability Concept | Delivery Analogy |
|---|---|
| SLI | Percentage of packages delivered within 2 days |
| SLO | Target: 99% delivered within 2 days |
| SLA | Contract promise to customers |
| Error budget | 1% of packages may be late |
| Burn rate | How quickly late deliveries are consuming the allowed 1% |

This is practical because some failures are unavoidable:

- Bad weather
- Traffic
- Wrong addresses
- Vehicle breakdowns
- Warehouse delays

Software systems have similar problems:

- Network failures
- Database overload
- Bad deployments
- Cloud provider incidents
- Traffic spikes
- Dependency failures

The goal is not perfection.

The goal is to define what “reliable enough” means.

## Technical Explanation

A **Service Level Indicator**, or **SLI**, is a specific metric that describes user-visible reliability.

Good SLIs usually measure things users care about, such as:

- Request success rate
- Request latency
- Availability
- Freshness of data
- Durability
- Correctness
- Throughput

For an API, common SLIs are:

```text
Availability SLI:
successful_requests / total_requests

Latency SLI:
requests_under_latency_threshold / total_requests
```

An **SLO** is the target value for an SLI over a specific time window.

Example:

```text
99.9% of HTTP requests to /api/orders should return non-5xx responses over a rolling 30-day window.
```

This SLO has several important parts:

| Part | Example |
|---|---|
| Service | Orders API |
| Endpoint | `/api/orders` |
| SLI | Percentage of non-5xx responses |
| Target | 99.9% |
| Time window | 30 days |

An **SLA** is different from an SLO.

An SLA is usually an external agreement with consequences if broken.

Example:

```text
If monthly availability drops below 99.9%, the customer receives service credits.
```

Not every SLO is an SLA.

Most internal SLOs are used for engineering decisions, not contracts.

An **error budget** is calculated from the SLO.

If your SLO is 99.9%, your allowed error rate is:

```text
100% - 99.9% = 0.1%
```

That 0.1% is the error budget.

If you are burning through the error budget too fast, it means the service is less reliable than intended.

Teams often use error budgets to make decisions:

```text
If error budget is healthy:
  Continue normal feature development.

If error budget is nearly exhausted:
  Reduce risky deployments.
  Prioritize reliability work.

If error budget is exhausted:
  Freeze high-risk launches.
  Fix incidents and systemic causes.
```

This connects directly to observability.

Metrics, logs, and traces help you understand system behavior, but SLOs tell you whether that behavior is acceptable.

Since the previous lesson covered distributed tracing, connect it like this:

```text
Tracing helps explain why requests are slow or failing.
SLOs define how much slowness or failure is acceptable.
```

## Practical Example

Let’s define one SLI and one SLO for an API endpoint.

Assume you own this endpoint:

```http
GET /api/orders/{order_id}
```

This endpoint is used by customers to view order details.

### Step 1: Define the user expectation

Users expect the endpoint to:

- Return successfully
- Return quickly
- Be available most of the time

For this example, we will focus on **availability**.

### Step 2: Define the SLI

A simple availability SLI could be:

```text
SLI:
Percentage of valid GET /api/orders/{order_id} requests that return a non-5xx HTTP response.
```

In formula form:

```text
SLI = non_5xx_responses / total_valid_requests
```

Example:

```text
total_valid_requests = 1,000,000
non_5xx_responses    = 999,200

SLI = 999,200 / 1,000,000
SLI = 99.92%
```

Important detail:

We usually count **5xx responses** as server failures.

We usually do not count normal **4xx responses** as availability failures because those are often client-side problems.

For example:

```text
404 Not Found     -> customer requested an order that does not exist
401 Unauthorized  -> customer is not logged in
400 Bad Request   -> invalid request format
500 Internal Error -> server failed
503 Unavailable   -> service unavailable
```

For this availability SLI, `500` and `503` count against the service.

### Step 3: Define the SLO

Now define the target:

```text
SLO:
99.9% of valid GET /api/orders/{order_id} requests should return a non-5xx response over a rolling 30-day window.
```

This means the service can fail up to:

```text
100% - 99.9% = 0.1%
```

### Step 4: Calculate the error budget

If the endpoint receives 2,000,000 valid requests in 30 days:

```text
Error budget = 0.1% of 2,000,000

0.001 * 2,000,000 = 2,000
```

So the endpoint can have up to:

```text
2,000 failed 5xx responses in 30 days
```

before it violates the SLO.

### Step 5: Example Prometheus-style query

If you had HTTP request metrics, they might look like this:

```text
http_requests_total{service="orders-api", route="/api/orders/:id", status="200"}
http_requests_total{service="orders-api", route="/api/orders/:id", status="500"}
http_requests_total{service="orders-api", route="/api/orders/:id", status="503"}
```

A simplified PromQL-style availability SLI might be:

```promql
sum(rate(http_requests_total{
  service="orders-api",
  route="/api/orders/:id",
  status!~"5.."
}[5m]))
/
sum(rate(http_requests_total{
  service="orders-api",
  route="/api/orders/:id"
}[5m]))
```

This calculates:

```text
rate of non-5xx requests / rate of all requests
```

For an SLO, you would evaluate this over a longer window, such as 30 days.

### Step 6: Add a latency SLI later

Availability alone is not enough.

A service could return `200 OK` but take 20 seconds. Users would still consider that bad.

A latency SLI could be:

```text
SLI:
Percentage of GET /api/orders/{order_id} requests completed in under 300ms.
```

A latency SLO could be:

```text
SLO:
95% of valid GET /api/orders/{order_id} requests should complete in under 300ms over a rolling 30-day window.
```

Most important production services have multiple SLOs.

Example:

```text
Availability SLO:
99.9% non-5xx over 30 days.

Latency SLO:
95% of requests under 300ms over 30 days.
```

## Official Documentation To Read

- [Google SRE Workbook — Implementing SLOs](https://sre.google/workbook/implementing-slos/)

## Good Reads

- [Google SRE Book](https://sre.google/sre-book/table-of-contents/)

## Where This Appears in Production

SLOs appear in many real production engineering activities.

### 1. Alerting

Good alerts are often based on SLO impact.

Instead of alerting on every small CPU spike, teams alert when user-visible reliability is at risk.

Example:

```text
Alert:
The orders API is burning error budget too quickly.
```

This is usually better than:

```text
Alert:
CPU is above 80%.
```

High CPU may or may not affect users.

SLO burn affects users directly.

### 2. Incident response

During an incident, teams ask:

```text
Are we violating the SLO?
How much error budget did we burn?
Which users were affected?
How long did the bad state last?
```

SLOs help measure incident severity.

### 3. Release decisions

If the service has plenty of error budget, the team may continue shipping.

If the service has almost no error budget left, the team may pause risky changes.

Example:

```text
The payments API has used 90% of its monthly error budget.
No high-risk deploys until reliability improves.
```

### 4. Platform engineering

Platform teams may define SLOs for internal systems such as:

- CI/CD pipelines
- Kubernetes clusters
- Internal developer portals
- Container registries
- Logging pipelines
- Metrics systems
- Secret management systems

Example internal SLO:

```text
99% of CI jobs should start within 2 minutes over 7 days.
```

### 5. Product planning

SLOs help product and engineering teams make tradeoffs.

If a team wants to improve reliability from 99.9% to 99.99%, that may require:

- More redundancy
- More testing
- More automation
- More infrastructure cost
- More operational complexity
- Slower feature delivery

SLOs make these tradeoffs visible.

### 6. Executive reporting

Leadership may ask:

```text
Is the service reliable?
Are customers affected?
Are we meeting our reliability targets?
```

SLOs provide a concrete answer.

## Common Beginner Mistakes

### 1. Confusing SLI, SLO, and SLA

These sound similar but mean different things.

```text
SLI = measurement
SLO = target
SLA = contract
```

Example:

```text
SLI:
99.92% of requests succeeded.

SLO:
99.9% of requests should succeed.

SLA:
If availability is below 99.9%, customers receive service credits.
```

### 2. Setting SLOs to 100%

100% reliability is usually a bad goal.

Why?

Because it usually requires extreme cost and slows down engineering.

Also, users may not notice the difference between:

```text
99.99% reliability
```

and

```text
99.999% reliability
```

for many systems.

Trying to achieve 100% can lead to:

- Over-engineering
- Fear of deployments
- Slow delivery
- Excessive infrastructure cost
- Burnout from too many alerts

The goal is not “never fail.”

The goal is “fail rarely enough that users are satisfied.”

### 3. Choosing infrastructure metrics as SLIs

CPU, memory, disk, and queue depth are useful signals, but they are usually not good user-facing SLIs by themselves.

Bad SLI:

```text
CPU should be below 70%.
```

Better SLI:

```text
99.9% of checkout requests should return successfully.
```

Infrastructure metrics help diagnose problems.

SLIs measure user experience.

### 4. Ignoring time windows

An SLO must have a time window.

Incomplete SLO:

```text
99.9% availability.
```

Better SLO:

```text
99.9% availability over a rolling 30-day window.
```

The time window matters because reliability is measured over time.

### 5. Measuring everything

You do not need an SLO for every endpoint.

Start with user-critical journeys:

- Login
- Checkout
- Payment
- Search
- Order creation
- Order lookup
- File upload
- API authentication

Too many SLOs create noise.

### 6. Treating all failures equally

A `500` on a critical payment endpoint may matter more than a `500` on an admin-only debug endpoint.

Not all requests have the same user impact.

Start with the most important user journeys.

### 7. Forgetting dependencies

Your service may depend on:

- Databases
- Caches
- Queues
- Third-party APIs
- Authentication providers
- Cloud services

If those fail, your SLO may be affected.

Ownership boundaries matter, but users usually care about the full experience.

### 8. Creating SLOs without action

An SLO is not useful if nothing happens when it is missed.

Every SLO should influence decisions.

Example:

```text
If the service burns more than 50% of its monthly error budget in one week,
review recent changes and prioritize reliability work.
```

## Related Concepts

- Reliability
- Availability
- Latency
- Error rate
- Error budget
- Burn rate
- Incident management
- Alerting
- Monitoring
- Observability
- Metrics
- Distributed tracing
- Logs
- SLAs
- Service ownership
- Production readiness
- Capacity planning
- Change management
- Post-incident review
- User journey monitoring
- Synthetic monitoring
- Golden signals
- RED metrics
- USE metrics

## Interview-Level Explanation

An **SLI** is a metric that measures service reliability from the user’s perspective, such as request success rate or latency.

An **SLO** is a target for that SLI over a defined time window, such as “99.9% of requests should succeed over 30 days.”

An **SLA** is a formal external agreement, often with business or financial consequences if the target is missed.

The **error budget** is the allowed amount of failure implied by the SLO. For example, a 99.9% SLO allows 0.1% failure.

Teams use error budgets to balance reliability and feature velocity. If the budget is healthy, teams can keep shipping. If the budget is exhausted, they should reduce risk and focus on reliability.

100% reliability is usually not the goal because it is extremely expensive, often impossible in distributed systems, and can slow down product delivery without meaningful user benefit.

## Hands-On Exercise

Use the provided task:

> Define one SLI and one SLO for an API endpoint.

### Scenario

Choose one API endpoint from a service you have worked on or can imagine.

Examples:

```http
GET /api/users/{id}
POST /api/orders
POST /api/payments
GET /api/search?q=...
POST /api/login
```

For this exercise, use one endpoint only.

### Step 1: Choose the endpoint

Write the endpoint:

```text
Endpoint:
GET /api/orders/{order_id}
```

### Step 2: Describe the user expectation

Answer:

```text
What does the user expect from this endpoint?
```

Example:

```text
Users expect to retrieve order details successfully and quickly.
```

### Step 3: Choose one SLI type

Pick one:

- Availability
- Latency
- Correctness
- Freshness
- Durability

For a first SLO, choose either **availability** or **latency**.

Example:

```text
SLI type:
Availability
```

### Step 4: Define the SLI

Write the SLI as a sentence.

Example:

```text
SLI:
The percentage of valid GET /api/orders/{order_id} requests that return a non-5xx HTTP response.
```

Then write it as a formula:

```text
SLI = non_5xx_responses / total_valid_requests
```

### Step 5: Define the SLO

Choose a target and a time window.

Example:

```text
SLO:
99.9% of valid GET /api/orders/{order_id} requests should return a non-5xx response over a rolling 30-day window.
```

### Step 6: Calculate the error budget

Use this formula:

```text
Error budget percentage = 100% - SLO target
```

Example:

```text
SLO target = 99.9%

Error budget = 100% - 99.9%
Error budget = 0.1%
```

Now calculate request count.

Assume:

```text
Total valid requests in 30 days = 500,000
```

Then:

```text
Allowed failures = 0.1% of 500,000
Allowed failures = 0.001 * 500,000
Allowed failures = 500
```

So your service can have up to:

```text
500 failed requests in 30 days
```

before missing the SLO.

### Step 7: Decide what happens if the SLO is at risk

Write one action rule.

Example:

```text
If the endpoint consumes more than 50% of its monthly error budget in one week,
the team should review recent deployments and prioritize reliability fixes.
```

### Step 8: Write your final answer

Use this template:

```markdown
## Endpoint

GET /api/orders/{order_id}

## User Expectation

Users expect to retrieve order details successfully and quickly.

## SLI

The percentage of valid GET /api/orders/{order_id} requests that return a non-5xx HTTP response.

Formula:

SLI = non_5xx_responses / total_valid_requests

## SLO

99.9% of valid GET /api/orders/{order_id} requests should return a non-5xx response over a rolling 30-day window.

## Error Budget

Error budget = 100% - 99.9% = 0.1%

If there are 500,000 valid requests in 30 days:

Allowed failures = 0.001 * 500,000 = 500

## Action Rule

If more than 50% of the monthly error budget is used in one week, pause risky changes and prioritize reliability work.
```

## Expected Outcome

After completing the exercise, you should be able to:

- Explain what an SLI is
- Explain what an SLO is
- Explain what an SLA is
- Calculate an error budget from an SLO
- Define one practical SLI for an API endpoint
- Define one practical SLO for an API endpoint
- Explain why 100% reliability is usually not the goal
- Connect SLOs to production decisions like alerting, deployments, and reliability work

You should be able to say something like:

```text
For GET /api/orders/{order_id}, I chose availability as the SLI.
The SLI is the percentage of valid requests that return a non-5xx response.
The SLO is 99.9% success over 30 days.
That gives us a 0.1% error budget.
If we receive 500,000 requests in 30 days, we can tolerate 500 server-side failures before violating the SLO.
```

## Quiz Questions

1. What is the difference between an SLI, an SLO, and an SLA?

2. If a service has a 99.95% availability SLO over 30 days, what is its error budget percentage?

3. Why is 100% reliability usually not a good target for most production systems?

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

Next, learn about **error budget burn rates and SLO-based alerting**.

That is the practical next step after defining SLOs.

Once you know the reliability target, you need to know:

- How fast the service is consuming the error budget
- When to alert
- Which alerts should page someone
- Which alerts should create a ticket
- How to avoid noisy alerts that do not represent real user impact
