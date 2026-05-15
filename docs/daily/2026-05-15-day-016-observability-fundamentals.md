# Day 016 — Observability Fundamentals

Date: 2026-05-15

## Phase

Phase 3 — Reliability and Observability

## Learning Objective

By the end of this lesson, you should understand the basic building blocks of observability:

- Logs
- Metrics
- Traces
- Spans
- Context propagation
- Telemetry pipelines

You should also understand why production systems need observability and how it helps engineers debug, operate, and improve real systems.

## Why This Topic Matters

In local development, debugging is often simple.

You can:

- Read the terminal output
- Add a print statement
- Use a debugger
- Restart the app quickly

In production, things are different.

A production system may have:

- Many services
- Many servers or containers
- Many users
- Background jobs
- Message queues
- Databases
- Third-party APIs
- Network failures
- Partial failures

When something breaks, you usually cannot pause the system and inspect it manually.

Observability gives you the information needed to answer questions like:

- Is the system healthy?
- What changed?
- Which service is failing?
- Which request failed?
- Why is latency high?
- Is the database slow?
- Is this affecting one user or everyone?
- Did the deployment cause the issue?

Without observability, production debugging becomes guessing.

With observability, production debugging becomes investigation.

## Simple Explanation

Observability means your system tells you what is happening inside it.

There are three major types of signals:

1. **Logs**
   - Text records of events.
   - Example: `"user_login_failed"` or `"payment_created"`.

2. **Metrics**
   - Numbers measured over time.
   - Example: request count, error rate, CPU usage, latency.

3. **Traces**
   - A path showing how one request moved through multiple services.
   - Example: API gateway → user service → payment service → database.

A simple way to think about it:

- **Logs** tell you what happened.
- **Metrics** tell you how often or how much it happened.
- **Traces** tell you where it happened across services.

Production systems need all three.

## Real-World Analogy

Think about a hospital.

A patient arrives with a problem.

The hospital uses different kinds of information:

- **Logs** are like doctor notes:
  - “Patient reported chest pain at 10:03.”
  - “Medication given at 10:10.”

- **Metrics** are like vital signs:
  - Heart rate
  - Blood pressure
  - Oxygen level
  - Temperature

- **Traces** are like the patient journey:
  - Emergency room → lab test → X-ray → specialist → pharmacy

Each signal answers a different question.

If you only have doctor notes, you may miss trends.

If you only have vital signs, you may not know what happened.

If you only have the patient journey, you may not know the details at each step.

Good diagnosis needs all three.

Production engineering is similar.

## Technical Explanation

Observability is the practice of collecting, processing, and analyzing telemetry data from software systems.

**Telemetry** means data emitted by your application or infrastructure about its behavior.

The three core telemetry signals are:

## 1. Logs

Logs are timestamped records of events.

Example:

```json
{
  "timestamp": "2026-05-15T10:15:30Z",
  "level": "INFO",
  "message": "order_created",
  "request_id": "req-123",
  "user_id": "user-456",
  "order_id": "order-789"
}
```

Good logs should be:

- Structured
- Searchable
- Consistent
- Useful during debugging
- Connected to a request or operation

Structured logs are usually JSON instead of plain text.

Bad log:

```text
Order created
```

Better log:

```json
{
  "level": "INFO",
  "event": "order_created",
  "request_id": "req-123",
  "order_id": "order-789"
}
```

The second log is easier for log systems to search and filter.

## 2. Metrics

Metrics are numeric measurements over time.

Examples:

```text
http_requests_total = 15234
http_request_duration_seconds = 0.183
http_errors_total = 42
cpu_usage_percent = 73
memory_usage_bytes = 824000000
```

Metrics are useful for dashboards and alerts.

Common production metrics include:

- Request rate
- Error rate
- Latency
- CPU usage
- Memory usage
- Queue depth
- Database connection count
- Cache hit rate

Metrics help answer:

- Is the service healthy?
- Is traffic increasing?
- Are errors increasing?
- Is latency getting worse?
- Should an alert fire?

## 3. Traces

A trace shows the full journey of a request through a system.

For example:

```text
Trace: request_id=req-123

Client
  -> API Gateway
      -> Auth Service
      -> Order Service
          -> Database
          -> Payment Service
              -> External Payment API
```

A trace is made of **spans**.

A **span** represents one operation inside a trace.

Example spans:

```text
Span 1: HTTP GET /checkout
Span 2: Validate user session
Span 3: Create order
Span 4: Insert order into database
Span 5: Call payment provider
```

Each span usually has:

- Trace ID
- Span ID
- Parent span ID
- Start time
- End time
- Duration
- Attributes/tags
- Status

Traces are especially useful in distributed systems because one user request may touch many services.

## 4. Context Propagation

Context propagation means passing request-related information across function calls, services, queues, and network boundaries.

Important context often includes:

- `request_id`
- `trace_id`
- `span_id`
- User or tenant identifiers
- Correlation IDs

Example:

```text
Client sends request
  request_id=req-123

API receives request
  logs request_id=req-123
  calls payment service with request_id=req-123

Payment service logs
  request_id=req-123

Database query logs
  request_id=req-123
```

Because every log line includes `request_id`, you can search for `req-123` and see everything that happened for that request.

Without context propagation, logs from different services are disconnected.

## 5. Telemetry Pipeline

A telemetry pipeline is the path telemetry data takes from your application to the place where engineers inspect it.

A common pipeline looks like this:

```text
Application
  -> OpenTelemetry SDK / logging library
  -> OpenTelemetry Collector or agent
  -> Backend storage
  -> Dashboards, alerts, and search tools
```

The pipeline may process:

- Logs
- Metrics
- Traces

It may also:

- Add metadata
- Filter sensitive data
- Sample high-volume traces
- Export data to observability platforms

OpenTelemetry is a standard way to collect and export telemetry data.

## Practical Example

Here is a small Python Flask app that adds structured logs and includes `request_id` in every log line.

### Example app

```python
from flask import Flask, request, jsonify, g
import logging
import json
import uuid
import time

app = Flask(__name__)

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", None),
            "path": getattr(record, "path", None),
            "method": getattr(record, "method", None),
        }
        return json.dumps(log_record)

logger = logging.getLogger("app")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logger.addHandler(handler)

def log_info(message):
    logger.info(
        message,
        extra={
            "request_id": getattr(g, "request_id", None),
            "path": request.path if request else None,
            "method": request.method if request else None,
        },
    )

@app.before_request
def assign_request_id():
    g.request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    g.start_time = time.time()

    log_info("request_started")

@app.after_request
def add_request_id_header(response):
    duration_ms = round((time.time() - g.start_time) * 1000, 2)

    logger.info(
        "request_finished",
        extra={
            "request_id": g.request_id,
            "path": request.path,
            "method": request.method,
            "duration_ms": duration_ms,
        },
    )

    response.headers["X-Request-ID"] = g.request_id
    return response

@app.route("/health")
def health():
    log_info("health_check")
    return jsonify({"status": "ok"})

@app.route("/orders", methods=["POST"])
def create_order():
    log_info("creating_order")

    # Simulate business logic
    order_id = str(uuid.uuid4())

    logger.info(
        "order_created",
        extra={
            "request_id": g.request_id,
            "path": request.path,
            "method": request.method,
            "order_id": order_id,
        },
    )

    return jsonify({
        "order_id": order_id,
        "request_id": g.request_id
    }), 201

if __name__ == "__main__":
    app.run(port=5000)
```

### Run the app

```bash
pip install flask
python app.py
```

### Call the app

```bash
curl -X POST http://localhost:5000/orders \
  -H "Content-Type: application/json" \
  -H "X-Request-ID: req-demo-123" \
  -d '{"item":"book"}'
```

### Example log output

```json
{"timestamp": "2026-05-15 10:00:01,123", "level": "INFO", "message": "request_started", "request_id": "req-demo-123", "path": "/orders", "method": "POST"}
{"timestamp": "2026-05-15 10:00:01,124", "level": "INFO", "message": "creating_order", "request_id": "req-demo-123", "path": "/orders", "method": "POST"}
{"timestamp": "2026-05-15 10:00:01,125", "level": "INFO", "message": "order_created", "request_id": "req-demo-123", "path": "/orders", "method": "POST"}
{"timestamp": "2026-05-15 10:00:01,126", "level": "INFO", "message": "request_finished", "request_id": "req-demo-123", "path": "/orders", "method": "POST"}
```

Now every log line for this request can be found by searching:

```text
req-demo-123
```

This is the beginning of request correlation.

## Official Documentation To Read

- [OpenTelemetry — What is OpenTelemetry?](https://opentelemetry.io/docs/what-is-opentelemetry/)
- [OpenTelemetry — Concepts](https://opentelemetry.io/docs/concepts/)

## Good Reads

- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)

## Where This Appears in Production

Observability appears everywhere in production systems.

Common examples:

## API Services

Backend APIs usually emit:

- Access logs
- Error logs
- Request latency metrics
- HTTP status code metrics
- Distributed traces

Example question:

```text
Why are POST /checkout requests failing?
```

Observability helps you inspect:

- Error rate
- Failing request logs
- Slow spans
- Database calls
- External API calls

## Kubernetes and Containers

Platform teams observe:

- Pod restarts
- CPU usage
- Memory usage
- Container logs
- Network errors
- Deployment changes

Example question:

```text
Did this service start failing after the latest deployment?
```

## Databases

Databases expose:

- Query latency
- Connection count
- Lock waits
- Replication lag
- Error logs

Example question:

```text
Is the API slow because the database is slow?
```

## Message Queues

Queues expose:

- Queue depth
- Consumer lag
- Processing failures
- Dead-letter queue count

Example question:

```text
Are background jobs falling behind?
```

## Incident Response

During incidents, engineers use observability to answer:

- What is broken?
- When did it start?
- Who is affected?
- What changed recently?
- Is the system recovering?

Good observability reduces time to detect and time to recover.

## Common Beginner Mistakes

1. **Only using plain text logs**

   Plain text logs are harder to search and analyze.

   Prefer structured logs like JSON.

2. **Not including request IDs**

   Without `request_id`, it is difficult to connect log lines from the same request.

3. **Logging too little**

   If logs only say `"error occurred"`, they are not useful.

   Include relevant context.

4. **Logging too much**

   Too many logs increase cost and make debugging noisy.

   Log important events, not every tiny detail.

5. **Logging sensitive data**

   Do not log:

   - Passwords
   - API keys
   - Access tokens
   - Credit card numbers
   - Personal data unless explicitly allowed and protected

6. **Confusing logs, metrics, and traces**

   They are related, but not the same.

   - Logs are events.
   - Metrics are numbers over time.
   - Traces are request journeys.

7. **Only adding observability after an incident**

   Observability should be part of normal development, not an emergency patch.

8. **Ignoring context propagation**

   If request context is lost between services, debugging distributed systems becomes much harder.

9. **Assuming dashboards are enough**

   Dashboards show known signals.

   Logs and traces help investigate unknown problems.

10. **Not standardizing field names**

   If one service logs `requestId`, another logs `request_id`, and another logs `correlationId`, searching becomes harder.

   Pick consistent names.

## Related Concepts

- Logging
- Structured logging
- Metrics
- Tracing
- Spans
- Trace ID
- Span ID
- Request ID
- Correlation ID
- Context propagation
- OpenTelemetry
- Telemetry pipeline
- Observability backend
- Dashboards
- Alerting
- SLOs
- SLIs
- Incident response
- Reliability engineering
- Distributed systems
- Service-to-service communication

## Interview-Level Explanation

Observability is the ability to understand what a system is doing by looking at the telemetry it produces.

The three main telemetry signals are logs, metrics, and traces.

Logs record discrete events, metrics measure numeric behavior over time, and traces show the path of a request through one or more services. A trace is made of spans, where each span represents one operation. Context propagation passes identifiers like trace IDs or request IDs across service boundaries so engineers can correlate telemetry.

In production, observability is essential for debugging, alerting, incident response, performance analysis, and reliability improvement.

## Hands-On Exercise

Use the provided hands-on task:

> Add structured logs to a small app and include `request_id` in every log line.

### Goal

Create or modify a small web app so every request gets a `request_id`, and every log line includes that same `request_id`.

### Step 1: Pick a small app

Use any simple backend app.

Good options:

- Python Flask
- Node.js Express
- Go HTTP server
- Java Spring Boot
- Ruby Sinatra

If you do not already have one, use the Flask example from this lesson.

### Step 2: Generate or read a request ID

For every incoming request:

- Check if the client sent `X-Request-ID`
- If yes, use it
- If no, generate a new UUID

Example behavior:

```text
Incoming header:
X-Request-ID: req-abc-123

Use:
request_id=req-abc-123
```

If the header is missing:

```text
Generate:
request_id=550e8400-e29b-41d4-a716-446655440000
```

### Step 3: Store request ID for the lifetime of the request

Store it somewhere request-scoped.

Examples:

- Flask: `g.request_id`
- Express: `req.requestId`
- Go: `context.Context`
- Java: MDC or request context

The important idea:

```text
Every function handling this request should be able to access the same request_id.
```

### Step 4: Change logs to structured JSON

Instead of this:

```text
Order created
```

Log this:

```json
{
  "level": "INFO",
  "event": "order_created",
  "request_id": "req-abc-123",
  "order_id": "order-789"
}
```

At minimum, include:

- Timestamp
- Level
- Message or event name
- `request_id`

Useful extra fields:

- HTTP method
- Path
- Status code
- Duration
- User ID
- Order ID
- Error message

### Step 5: Log request start and finish

Add logs like:

```json
{
  "level": "INFO",
  "event": "request_started",
  "request_id": "req-abc-123",
  "method": "POST",
  "path": "/orders"
}
```

And:

```json
{
  "level": "INFO",
  "event": "request_finished",
  "request_id": "req-abc-123",
  "method": "POST",
  "path": "/orders",
  "status": 201,
  "duration_ms": 34.8
}
```

### Step 6: Add at least one business log

Example:

```json
{
  "level": "INFO",
  "event": "order_created",
  "request_id": "req-abc-123",
  "order_id": "order-789"
}
```

### Step 7: Test with curl

Send a request with a known request ID:

```bash
curl -X POST http://localhost:5000/orders \
  -H "Content-Type: application/json" \
  -H "X-Request-ID: req-test-001" \
  -d '{"item":"book"}'
```

Then confirm every related log line contains:

```text
req-test-001
```

### Step 8: Test without a request ID

Send a request without `X-Request-ID`:

```bash
curl http://localhost:5000/health
```

Confirm the app generates a new request ID and includes it in every log line.

### Step 9: Return request ID to the client

Add this response header:

```text
X-Request-ID: <request_id>
```

This helps clients report issues with a specific request ID.

### Step 10: Write down what you observed

Answer:

- What log fields did you include?
- How did you generate the request ID?
- How did you ensure every log line had it?
- How would this help in production debugging?

## Expected Outcome

After this exercise, you should be able to:

- Explain what observability means
- Describe the difference between logs, metrics, and traces
- Explain what a span is
- Explain why request IDs and trace IDs matter
- Explain context propagation in simple terms
- Add structured JSON logs to a small app
- Include `request_id` in every log line
- Use logs to follow one request through an application
- Describe a basic telemetry pipeline from application to observability backend

You should be able to say:

```text
I added structured logs to my app. Each request gets a request_id from the X-Request-ID header or from a generated UUID. Every log line includes that request_id, so I can search logs and follow one request from start to finish.
```

## Quiz Questions

1. What is the difference between logs, metrics, and traces?

2. Why is `request_id` useful when debugging a production issue?

3. What is a span, and how does it relate to a trace?

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

Next, learn **metrics and alerting fundamentals**.

A good next step is to understand how production teams measure service health using metrics like request rate, error rate, and latency, then use those metrics to build dashboards and alerts.
