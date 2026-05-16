# Day 017 — Distributed Tracing

Date: 2026-05-16

## Phase

Phase 3 — Reliability and Observability

## Learning Objective

By the end of this lesson, you should understand how distributed traces follow a single request across multiple services.

You should be able to explain:

- What a trace is
- What a span is
- How spans form parent-child relationships
- What a trace ID is
- What context propagation means
- Why tracing is useful when debugging production systems

## Why This Topic Matters

Modern backend systems are often split into many services.

A single user request might pass through:

```text
Browser
  → API Gateway
  → Auth Service
  → Order Service
  → Payment Service
  → Database
  → Message Queue
```

If the request is slow or fails, logs from one service are not enough.

You need to answer questions like:

- Which service was slow?
- Did the request reach the payment service?
- Which downstream call failed?
- Was the database query the problem?
- Did the same request produce errors in multiple services?
- How long did each service spend handling the request?

Distributed tracing helps answer these questions by connecting work across services into one request timeline.

In production engineering, tracing is one of the most useful tools for debugging latency, failures, and complex request flows.

## Simple Explanation

A distributed trace is a record of one request as it moves through a system.

Each piece of work done by a service is called a span.

For example:

```text
Trace: checkout request

Span 1: API receives checkout request
Span 2: API calls Order Service
Span 3: Order Service validates cart
Span 4: Order Service calls Payment Service
Span 5: Payment Service charges card
Span 6: Order Service saves order
```

All of these spans belong to the same trace.

The trace shows the full journey of the request.

The most important idea:

```text
A trace is the whole request journey.
A span is one operation inside that journey.
```

A trace ID connects all spans for the same request.

Context propagation is how one service passes tracing information to the next service.

Without context propagation, each service may create its own separate trace, and you lose the full request story.

Previous feedback did not include a specific confusion to address, so today we will be extra explicit about the difference between traces, spans, and trace context.

## Real-World Analogy

Imagine a package delivery.

The package moves through many locations:

```text
Customer
  → Local Post Office
  → Regional Sorting Center
  → Airport
  → Destination Sorting Center
  → Delivery Truck
  → Final Address
```

Each location scans the package.

The tracking number connects all scans together.

In distributed tracing:

- The package is the request
- Each scan is a span
- The tracking number is the trace ID
- Passing the tracking number to the next location is context propagation

If one location forgets to scan the package or loses the tracking number, the delivery history becomes incomplete.

That is similar to a service failing to propagate trace context.

## Technical Explanation

Distributed tracing tracks a request across process, network, and service boundaries.

The main concepts are:

### Trace

A trace represents the full path of one request or workflow.

Example:

```text
Trace ID: 4bf92f3577b34da6a3ce929d0e0e4736

GET /checkout
  → POST /orders
  → POST /payments
  → INSERT order into database
```

A trace contains one or more spans.

### Span

A span represents one unit of work.

A span usually has:

- A span ID
- A trace ID
- A parent span ID, unless it is the root span
- A start time
- An end time
- A duration
- Attributes, also called metadata
- Events
- Status, such as success or error

Example span:

```text
Span name: POST /payments
Trace ID: 4bf92f3577b34da6a3ce929d0e0e4736
Span ID: 00f067aa0ba902b7
Parent Span ID: b7ad6b7169203331
Duration: 230ms
Status: OK
```

### Parent-Child Relationships

Spans are connected in a tree.

Example:

```text
Trace: checkout request

Root span: GET /checkout
├── Child span: validate user session
├── Child span: POST /orders
│   ├── Child span: validate cart
│   ├── Child span: POST /payments
│   │   └── Child span: call payment provider
│   └── Child span: INSERT order
└── Child span: return response
```

This structure lets you see where time was spent.

If the checkout request took 2 seconds, tracing can show whether the time was spent in:

- The API service
- The order service
- The payment service
- The database
- A third-party API
- Network waiting time

### Trace ID

The trace ID identifies the entire trace.

Every span in the same request journey has the same trace ID.

Example:

```text
Trace ID: abc123

Service A span: trace_id=abc123
Service B span: trace_id=abc123
Service C span: trace_id=abc123
```

If Service B does not receive the trace context, it might create a new trace ID:

```text
Service A span: trace_id=abc123
Service B span: trace_id=xyz789
Service C span: trace_id=xyz789
```

Now the full journey is broken into separate traces.

That makes debugging harder.

### Context Propagation

Context propagation is the mechanism used to pass trace information between services.

For HTTP systems, this usually happens through request headers.

A common header is:

```text
traceparent
```

Example:

```text
traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
```

This header carries tracing information so the next service can continue the same trace instead of starting a new one.

In simple terms:

```text
Service A receives request.
Service A creates or continues a trace.
Service A calls Service B.
Service A sends trace context in HTTP headers.
Service B reads those headers.
Service B creates a child span under the same trace.
```

### Why OpenTelemetry Matters

OpenTelemetry provides a standard way to generate, collect, and export telemetry data.

For tracing, OpenTelemetry helps with:

- Creating spans
- Tracking active context
- Propagating context across services
- Adding attributes to spans
- Exporting traces to a backend system

A tracing backend might include systems such as Jaeger, Zipkin, Grafana Tempo, Honeycomb, Datadog, New Relic, or others.

The important part is that your application emits traces in a consistent way.

## Practical Example

Imagine two services:

```text
client
  → service-a
  → service-b
```

`service-a` receives the original request.

Then `service-a` calls `service-b`.

We want one trace that includes both services.

Expected trace shape:

```text
Trace: GET /start

Span: service-a GET /start
└── Span: service-a call service-b
    └── Span: service-b GET /work
```

### Example Using Simple HTTP Headers

This example uses plain code to show the idea before adding real OpenTelemetry instrumentation.

#### service-a.js

```js
const express = require("express");
const crypto = require("crypto");

const app = express();

function generateId(bytes) {
  return crypto.randomBytes(bytes).toString("hex");
}

app.get("/start", async (req, res) => {
  const traceId = req.headers["x-trace-id"] || generateId(16);
  const spanId = generateId(8);

  console.log({
    service: "service-a",
    route: "GET /start",
    traceId,
    spanId,
    parentSpanId: req.headers["x-parent-span-id"] || null,
  });

  const response = await fetch("http://localhost:3001/work", {
    headers: {
      "x-trace-id": traceId,
      "x-parent-span-id": spanId,
    },
  });

  const data = await response.json();

  res.json({
    service: "service-a",
    traceId,
    downstream: data,
  });
});

app.listen(3000, () => {
  console.log("service-a listening on port 3000");
});
```

#### service-b.js

```js
const express = require("express");
const crypto = require("crypto");

const app = express();

function generateId(bytes) {
  return crypto.randomBytes(bytes).toString("hex");
}

app.get("/work", (req, res) => {
  const traceId = req.headers["x-trace-id"] || generateId(16);
  const parentSpanId = req.headers["x-parent-span-id"] || null;
  const spanId = generateId(8);

  console.log({
    service: "service-b",
    route: "GET /work",
    traceId,
    spanId,
    parentSpanId,
  });

  res.json({
    service: "service-b",
    traceId,
    spanId,
    parentSpanId,
  });
});

app.listen(3001, () => {
  console.log("service-b listening on port 3001");
});
```

Run both services:

```bash
node service-b.js
node service-a.js
```

Call `service-a`:

```bash
curl http://localhost:3000/start
```

You should see both services log the same `traceId`.

Example logs:

```text
service-a:
{
  service: 'service-a',
  route: 'GET /start',
  traceId: '8e2f7a9c6d4b1e5f0123456789abcdef',
  spanId: '1111222233334444',
  parentSpanId: null
}

service-b:
{
  service: 'service-b',
  route: 'GET /work',
  traceId: '8e2f7a9c6d4b1e5f0123456789abcdef',
  spanId: 'aaaa5555bbbb6666',
  parentSpanId: '1111222233334444'
}
```

This is not full OpenTelemetry yet, but it demonstrates the core idea:

```text
The trace ID follows the request.
Each service creates its own span.
The downstream span points back to the upstream parent span.
```

In real OpenTelemetry instrumentation, this is usually handled through standard trace context headers and instrumentation libraries instead of custom `x-trace-id` headers.

## Official Documentation To Read

- [OpenTelemetry — Traces](https://opentelemetry.io/docs/concepts/signals/traces/)
- [OpenTelemetry — Context propagation](https://opentelemetry.io/docs/concepts/context-propagation/)

## Good Reads

- [OpenTelemetry — Observability primer](https://opentelemetry.io/docs/concepts/observability-primer/)

## Where This Appears in Production

Distributed tracing appears in many production systems.

Common examples:

### API Request Debugging

A user reports checkout is slow.

Tracing shows:

```text
GET /checkout: 2.4s
├── Auth check: 40ms
├── Order Service: 120ms
├── Payment Service: 2.1s
└── Database write: 30ms
```

Now you know the payment path is the bottleneck.

### Microservices

In microservice systems, one request often crosses many services.

Tracing helps teams understand service-to-service behavior.

### API Gateways

API gateways often start or continue traces.

They may add trace context before forwarding requests to backend services.

### Kubernetes Workloads

In Kubernetes, tracing is useful because requests may flow through many pods.

A trace can show:

```text
ingress
  → frontend pod
  → backend pod
  → cache
  → database
```

### Message Queues

Tracing can also follow asynchronous workflows.

Example:

```text
API receives request
  → publishes message
  → worker consumes message
  → worker calls another service
```

Context propagation is more complex with queues because the trace context must be included in message metadata or payload headers.

### Incident Response

During incidents, traces help engineers quickly identify:

- The failing dependency
- The slow service
- The request path
- Whether errors are isolated or widespread
- Whether retries are increasing latency

### SLO and Latency Analysis

Tracing helps explain why latency objectives are being missed.

Metrics may tell you:

```text
p95 latency is too high
```

Tracing can show:

```text
p95 latency is high because payment-provider calls are slow
```

## Common Beginner Mistakes

### 1. Thinking Logs and Traces Are the Same

Logs are individual event records.

Traces show the journey of a request across services.

They work best together.

Example:

```text
Trace shows where the failure happened.
Logs explain what the service was doing at that moment.
```

### 2. Forgetting Context Propagation

If Service A calls Service B but does not pass trace context, Service B starts a new trace.

That breaks the request timeline.

Bad:

```text
Service A trace_id=abc
Service B trace_id=xyz
```

Good:

```text
Service A trace_id=abc
Service B trace_id=abc
```

### 3. Creating Too Many Spans

Not every tiny function needs its own span.

Useful spans usually represent meaningful work:

- HTTP request
- Database query
- Cache call
- Queue publish
- External API call
- Expensive business operation

Too many spans can make traces noisy and expensive.

### 4. Creating Too Few Spans

If you only trace the initial request, you cannot see where time is spent.

A useful trace should include important downstream operations.

### 5. Not Adding Useful Attributes

A span without useful metadata is less helpful.

Useful attributes may include:

- HTTP method
- Route
- Status code
- Service name
- Database operation
- Queue name
- Error details
- Retry count

Be careful not to add sensitive data.

### 6. Putting Secrets or Personal Data in Spans

Do not put these in trace attributes:

- Passwords
- Tokens
- API keys
- Full credit card numbers
- Sensitive personal information
- Private customer data

Telemetry often gets stored and searched by many people and systems.

### 7. Assuming Tracing Fixes the System

Tracing does not fix failures.

Tracing helps you see where failures and latency happen.

You still need good engineering practices:

- Timeouts
- Retries with backoff
- Circuit breakers
- Load shedding
- Proper error handling
- Capacity planning

### 8. Ignoring Sampling

High-traffic systems may not store every trace.

Sampling controls which traces are kept.

This reduces cost and storage usage.

However, bad sampling configuration can cause you to miss important traces.

## Related Concepts

- Observability
- Metrics
- Logs
- Traces
- Spans
- Trace IDs
- Span IDs
- Parent span IDs
- Context propagation
- OpenTelemetry
- Instrumentation
- Sampling
- Service-to-service communication
- HTTP headers
- API gateways
- Microservices
- Distributed systems
- Latency analysis
- Incident response
- SLOs and SLIs
- Error budgets

## Interview-Level Explanation

Distributed tracing tracks a single request as it moves across multiple services.

A trace represents the full request journey. A span represents one operation within that journey. Spans share the same trace ID and are connected using parent-child relationships. Context propagation passes trace information, often through HTTP headers, so downstream services can create child spans instead of starting unrelated traces.

Tracing is useful because it helps engineers debug latency and failures in distributed systems by showing where time was spent and which dependency caused a problem.

## Hands-On Exercise

Instrument two small services and pass a trace context between them.

The goal is to see one request flow through two services while keeping the same trace identity.

### Step 1: Create a Project Directory

```bash
mkdir distributed-tracing-demo
cd distributed-tracing-demo
npm init -y
npm install express
```

### Step 2: Create `service-a.js`

Create a file named `service-a.js`.

```js
const express = require("express");
const crypto = require("crypto");

const app = express();

function generateId(bytes) {
  return crypto.randomBytes(bytes).toString("hex");
}

app.get("/start", async (req, res) => {
  const traceId = req.headers["x-trace-id"] || generateId(16);
  const spanId = generateId(8);
  const parentSpanId = req.headers["x-parent-span-id"] || null;

  const startTime = Date.now();

  console.log("START span", {
    service: "service-a",
    spanName: "GET /start",
    traceId,
    spanId,
    parentSpanId,
  });

  const downstreamResponse = await fetch("http://localhost:3001/work", {
    headers: {
      "x-trace-id": traceId,
      "x-parent-span-id": spanId,
    },
  });

  const downstreamData = await downstreamResponse.json();

  const durationMs = Date.now() - startTime;

  console.log("END span", {
    service: "service-a",
    spanName: "GET /start",
    traceId,
    spanId,
    durationMs,
  });

  res.json({
    service: "service-a",
    traceId,
    spanId,
    downstream: downstreamData,
  });
});

app.listen(3000, () => {
  console.log("service-a listening on port 3000");
});
```

### Step 3: Create `service-b.js`

Create a file named `service-b.js`.

```js
const express = require("express");
const crypto = require("crypto");

const app = express();

function generateId(bytes) {
  return crypto.randomBytes(bytes).toString("hex");
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

app.get("/work", async (req, res) => {
  const traceId = req.headers["x-trace-id"] || generateId(16);
  const parentSpanId = req.headers["x-parent-span-id"] || null;
  const spanId = generateId(8);

  const startTime = Date.now();

  console.log("START span", {
    service: "service-b",
    spanName: "GET /work",
    traceId,
    spanId,
    parentSpanId,
  });

  await sleep(200);

  const durationMs = Date.now() - startTime;

  console.log("END span", {
    service: "service-b",
    spanName: "GET /work",
    traceId,
    spanId,
    parentSpanId,
    durationMs,
  });

  res.json({
    service: "service-b",
    traceId,
    spanId,
    parentSpanId,
    durationMs,
  });
});

app.listen(3001, () => {
  console.log("service-b listening on port 3001");
});
```

### Step 4: Start `service-b`

In terminal 1:

```bash
node service-b.js
```

### Step 5: Start `service-a`

In terminal 2:

```bash
node service-a.js
```

### Step 6: Send a Request

In terminal 3:

```bash
curl http://localhost:3000/start
```

### Step 7: Inspect the Logs

Look at the logs from both services.

Confirm that:

- Both services have the same `traceId`
- `service-a` has a `spanId`
- `service-b` has its own `spanId`
- `service-b.parentSpanId` equals `service-a.spanId`

You should be able to draw this:

```text
Trace ID: same value in both services

service-a span
└── service-b span
```

### Step 8: Break Context Propagation on Purpose

In `service-a.js`, temporarily remove the headers from the `fetch` call:

```js
const downstreamResponse = await fetch("http://localhost:3001/work");
```

Restart `service-a`.

Call the endpoint again:

```bash
curl http://localhost:3000/start
```

Now inspect the logs.

You should see that `service-b` creates a different `traceId`.

This demonstrates what happens when trace context is not propagated.

### Step 9: Restore Context Propagation

Put the headers back:

```js
const downstreamResponse = await fetch("http://localhost:3001/work", {
  headers: {
    "x-trace-id": traceId,
    "x-parent-span-id": spanId,
  },
});
```

Restart `service-a`.

Run the request again and verify both services share the same trace ID.

### Step 10: Connect This to Real OpenTelemetry

Your demo used custom headers:

```text
x-trace-id
x-parent-span-id
```

Real OpenTelemetry uses standard context propagation mechanisms.

The important lesson is the same:

```text
Trace context must travel with the request.
```

In real systems, instrumentation libraries usually handle this for you, but you still need to understand what is happening.

## Expected Outcome

After completing the exercise, you should be able to explain:

- A trace is the full journey of a request
- A span is one unit of work inside a trace
- A trace ID connects all spans for the same request
- A span ID identifies one operation
- A parent span ID connects child spans to parent spans
- Context propagation passes trace information between services
- Without context propagation, traces become fragmented
- Distributed tracing helps debug latency and failures across services

You should also be able to look at simple logs and identify whether two services are part of the same trace.

## Quiz Questions

1. What is the difference between a trace and a span?

2. Why does `service-b` need to receive trace context from `service-a`?

3. If two services produce different trace IDs for the same user request, what likely went wrong?

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

Next, learn about metrics-based reliability signals such as latency, traffic, errors, and saturation. This connects tracing to production reliability by helping you understand both the high-level system health and the detailed request path behind problems.
