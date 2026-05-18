# Day 019 — Load Balancing

Date: 2026-05-18

## Phase

Phase 4 — System Design and Production

## Learning Objective

By the end of this lesson, you should understand how traffic is distributed across multiple backend instances.

You should be able to explain:

- What a load balancer does
- How round-robin load balancing works
- Why reverse proxies are commonly used in production
- How health checks help remove broken backend instances
- What sticky sessions are
- What happens when one backend instance fails

## Why This Topic Matters

Most real production systems do not run on a single backend server.

A production API usually has multiple copies of the same service running at the same time:

```text
Client
  |
  v
Load Balancer
  |
  +--> Backend Instance 1
  +--> Backend Instance 2
  +--> Backend Instance 3
```

This matters because one backend instance may not be enough to handle real traffic.

Load balancing helps with:

- **Scalability** — more backend instances can handle more requests
- **Availability** — if one instance fails, traffic can go to healthy ones
- **Deployments** — new versions can be rolled out gradually
- **Reliability** — traffic is spread instead of overwhelming one server
- **Operations** — platform teams can manage routing, TLS, health checks, and failover centrally

Without load balancing, a single backend server becomes a bottleneck and a single point of failure.

## Simple Explanation

A load balancer sits in front of multiple backend servers.

Instead of clients calling one backend directly, clients call the load balancer.

The load balancer then chooses which backend should handle each request.

Example:

```text
Request 1 -> Backend A
Request 2 -> Backend B
Request 3 -> Backend A
Request 4 -> Backend B
```

This is called **round-robin** when requests are distributed in order across available backends.

The client usually does not know which backend handled the request.

To the client, it looks like one system.

## Real-World Analogy

Imagine a grocery store with multiple checkout counters.

Customers enter the store and are directed to an available cashier.

```text
Customers
   |
   v
Store greeter / queue manager
   |
   +--> Cashier 1
   +--> Cashier 2
   +--> Cashier 3
```

The queue manager is like the load balancer.

If Cashier 2 goes on break, the queue manager stops sending customers there.

If the store gets busy, the manager can open more checkout counters.

That is similar to adding more backend instances behind a load balancer.

## Technical Explanation

A load balancer receives network traffic and forwards it to one of several backend targets.

In backend engineering, this usually happens at one of these layers:

### Layer 4 Load Balancing

Layer 4 load balancing works at the transport layer.

It routes based on information like:

- IP address
- TCP port
- UDP port

It does not usually inspect HTTP paths, headers, or cookies.

Example:

```text
TCP request on port 443 -> backend instance
```

### Layer 7 Load Balancing

Layer 7 load balancing works at the application layer.

It understands protocols like HTTP and HTTPS.

It can route based on:

- URL path
- Host header
- HTTP method
- Cookies
- Headers

Example:

```text
/api/users     -> user-service
/api/payments  -> payment-service
/admin         -> admin-service
```

NGINX is commonly used as a Layer 7 reverse proxy and load balancer.

### Reverse Proxy

A **reverse proxy** accepts requests from clients and forwards them to backend servers.

The client talks to the reverse proxy, not directly to the backend service.

```text
Client -> NGINX -> Backend
```

A reverse proxy can handle:

- Load balancing
- TLS termination
- Request routing
- Compression
- Caching
- Authentication integration
- Rate limiting
- Logging

### Round-Robin

Round-robin means the load balancer sends requests to backend servers in sequence.

Example with two backends:

```text
Request 1 -> backend-1
Request 2 -> backend-2
Request 3 -> backend-1
Request 4 -> backend-2
```

This is simple and common.

However, round-robin assumes all backend instances are roughly equal in capacity and health.

### Health Checks

A health check is a request used to determine whether a backend instance is healthy.

For example:

```http
GET /health
```

A healthy backend might return:

```http
200 OK
```

An unhealthy backend might return:

```http
500 Internal Server Error
```

Or it may not respond at all.

In production, load balancers use health checks to avoid sending traffic to broken instances.

Important distinction:

- **Passive failure handling**: the load balancer notices failures during real requests
- **Active health checks**: the load balancer regularly checks backend health using a configured endpoint

### Sticky Sessions

Sticky sessions mean the same client keeps getting routed to the same backend instance.

Example:

```text
User A -> backend-1
User A -> backend-1
User A -> backend-1

User B -> backend-2
User B -> backend-2
```

This can be useful if the backend stores session data in memory.

However, sticky sessions can create problems:

- Uneven traffic distribution
- Harder scaling
- More complicated failover
- Users may lose session state if their backend dies

A more scalable design stores session state outside the backend, such as in Redis or a database.

### Failure Handling

If one backend fails, a good load balancer should stop sending traffic to it.

Example before failure:

```text
NGINX
  +--> backend-1 healthy
  +--> backend-2 healthy
```

Example after `backend-2` fails:

```text
NGINX
  +--> backend-1 healthy
  +--> backend-2 unhealthy
```

Traffic should continue going to `backend-1`.

This does not mean users will never see errors. If a request is already in progress when a backend fails, that request may still fail.

Load balancing improves availability, but it does not magically eliminate all failure.

## Practical Example

Here is a small local example using NGINX as a reverse proxy and load balancer in front of two backend containers.

Architecture:

```text
curl localhost:8080
        |
        v
      NGINX
        |
        +--> backend1:3000
        +--> backend2:3000
```

Create a project directory:

```bash
mkdir nginx-load-balancing-demo
cd nginx-load-balancing-demo
```

Create this file:

```bash
touch docker-compose.yml nginx.conf app.js Dockerfile
```

Add the backend application.

`app.js`:

```js
const http = require("http");

const instanceName = process.env.INSTANCE_NAME || "unknown-instance";
const port = process.env.PORT || 3000;

const server = http.createServer((req, res) => {
  if (req.url === "/health") {
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ status: "ok", instance: instanceName }));
    return;
  }

  res.writeHead(200, { "Content-Type": "application/json" });
  res.end(
    JSON.stringify({
      message: "Hello from backend",
      instance: instanceName,
      path: req.url,
    })
  );
});

server.listen(port, () => {
  console.log(`${instanceName} listening on port ${port}`);
});
```

Add the Dockerfile.

`Dockerfile`:

```Dockerfile
FROM node:22-alpine

WORKDIR /app

COPY app.js .

EXPOSE 3000

CMD ["node", "app.js"]
```

Add the NGINX config.

`nginx.conf`:

```nginx
events {}

http {
    upstream backend_pool {
        server backend1:3000;
        server backend2:3000;
    }

    server {
        listen 80;

        location / {
            proxy_pass http://backend_pool;

            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }
    }
}
```

Add Docker Compose.

`docker-compose.yml`:

```yaml
services:
  backend1:
    build: .
    environment:
      INSTANCE_NAME: backend1

  backend2:
    build: .
    environment:
      INSTANCE_NAME: backend2

  nginx:
    image: nginx:1.27-alpine
    ports:
      - "8080:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - backend1
      - backend2
```

Start everything:

```bash
docker compose up --build
```

In another terminal, send several requests:

```bash
curl http://localhost:8080
curl http://localhost:8080
curl http://localhost:8080
curl http://localhost:8080
```

You should see responses alternating between backend instances:

```json
{"message":"Hello from backend","instance":"backend1","path":"/"}
```

```json
{"message":"Hello from backend","instance":"backend2","path":"/"}
```

You can also run:

```bash
for i in {1..10}; do curl -s http://localhost:8080; echo; done
```

You should see traffic distributed across both backend containers.

Now simulate a failure:

```bash
docker compose stop backend2
```

Send requests again:

```bash
for i in {1..10}; do curl -s http://localhost:8080; echo; done
```

You should see traffic go only to `backend1`, though depending on timing and connection reuse, you may briefly see an error while NGINX detects the failure.

Restart the failed backend:

```bash
docker compose start backend2
```

Try again:

```bash
for i in {1..10}; do curl -s http://localhost:8080; echo; done
```

Traffic should resume going to both backend instances.

## Official Documentation To Read

- [NGINX — HTTP Load Balancing](https://docs.nginx.com/nginx/admin-guide/load-balancer/http-load-balancer/)

## Good Reads

- [AWS — Elastic Load Balancing Documentation](https://docs.aws.amazon.com/elasticloadbalancing/)

## Where This Appears in Production

Load balancing appears almost everywhere in production systems.

Common places include:

### Public Application Entry Points

```text
Internet -> Load Balancer -> Web/API servers
```

Example:

A public API may expose one DNS name like:

```text
api.example.com
```

Behind that name, there may be many backend instances.

### Kubernetes

In Kubernetes, load balancing appears through:

- Services
- Ingress controllers
- Cloud load balancers
- Service meshes

Example:

```text
Client -> Cloud Load Balancer -> Ingress -> Service -> Pods
```

### Microservices

Internal services also use load balancing.

Example:

```text
payment-service -> user-service replicas
```

The caller may not know which exact `user-service` instance handles the request.

### Blue-Green and Canary Deployments

Load balancers can shift traffic between versions.

Example:

```text
95% traffic -> version 1
5% traffic  -> version 2
```

This helps teams test new versions safely.

### High Availability Systems

If a server, container, VM, or availability zone fails, load balancers help route traffic to healthy capacity.

Example:

```text
Load Balancer
  +--> us-east-1a backend instances
  +--> us-east-1b backend instances
  +--> us-east-1c backend instances
```

### TLS Termination

Many production load balancers terminate HTTPS.

That means:

```text
Client --HTTPS--> Load Balancer --HTTP or HTTPS--> Backend
```

This centralizes certificate management.

## Common Beginner Mistakes

### 1. Thinking Load Balancing Means No Failures

Load balancing reduces the impact of failures, but it does not remove all failures.

Requests can still fail if:

- All backends are unhealthy
- The load balancer is misconfigured
- A backend dies during a request
- The database is down
- The network is degraded

### 2. Confusing Reverse Proxy and Forward Proxy

A **reverse proxy** protects and fronts servers.

```text
Client -> Reverse Proxy -> Backend Server
```

A **forward proxy** is used by clients to reach the internet.

```text
Client -> Forward Proxy -> Internet
```

For backend production systems, load balancers often act as reverse proxies.

### 3. Forgetting Health Checks

If a load balancer does not know a backend is unhealthy, it may keep sending traffic to it.

Health checks should be simple and reliable.

A common health endpoint is:

```text
GET /health
```

But in production, be careful. A health check that does too much can cause problems.

### 4. Making Health Checks Too Shallow

A health check that only says “process is running” may not be enough.

For example, your app may be running but unable to connect to the database.

There are usually different types of checks:

- **Liveness** — is the process alive?
- **Readiness** — is the service ready to receive traffic?
- **Dependency health** — can the service reach required dependencies?

### 5. Using Sticky Sessions Without Understanding the Tradeoff

Sticky sessions can hide bad application design.

If your service stores user sessions only in memory, scaling becomes harder.

Better production designs often move session state to external storage.

### 6. Assuming Round-Robin Always Means Equal Load

Round-robin distributes requests, not necessarily work.

One request may take 5 milliseconds.

Another request may take 10 seconds.

So equal request count does not always mean equal backend load.

### 7. Not Passing Forwarded Headers

When using a reverse proxy, the backend may see the proxy IP instead of the real client IP.

Headers like these are commonly used:

```nginx
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
```

Applications and logging systems often need these headers for observability and debugging.

## Related Concepts

- Reverse proxy
- Forward proxy
- Round-robin routing
- Weighted round-robin
- Least connections
- Health checks
- Liveness checks
- Readiness checks
- Sticky sessions
- Session storage
- Horizontal scaling
- High availability
- Failover
- TLS termination
- DNS load balancing
- API gateways
- Kubernetes Services
- Kubernetes Ingress
- Service discovery
- Blue-green deployments
- Canary deployments
- Observability
- SLOs and error budgets

## Interview-Level Explanation

A load balancer distributes incoming traffic across multiple backend instances. It improves scalability and availability by preventing a single server from handling all requests.

In simple round-robin load balancing, requests are sent to each backend in sequence. A reverse proxy like NGINX can sit in front of backend services and forward requests to an upstream pool.

In production, load balancers usually use health checks to avoid routing traffic to unhealthy instances. Some systems use sticky sessions so the same client keeps going to the same backend, but this can make scaling and failover harder. A better design often keeps application instances stateless and stores shared state externally.

Load balancing helps with failure handling, but it does not eliminate failures completely. If all backends are unhealthy or a dependency like the database fails, users can still experience errors.

## Hands-On Exercise

Run two backend containers and put NGINX in front of them as a load balancer.

### Step 1: Create the Project

```bash
mkdir nginx-load-balancing-demo
cd nginx-load-balancing-demo
```

Create four files:

```bash
touch app.js Dockerfile nginx.conf docker-compose.yml
```

### Step 2: Add the Backend App

Put this in `app.js`:

```js
const http = require("http");

const instanceName = process.env.INSTANCE_NAME || "unknown-instance";
const port = process.env.PORT || 3000;

const server = http.createServer((req, res) => {
  if (req.url === "/health") {
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ status: "ok", instance: instanceName }));
    return;
  }

  res.writeHead(200, { "Content-Type": "application/json" });
  res.end(
    JSON.stringify({
      message: "Hello from backend",
      instance: instanceName,
      path: req.url,
      timestamp: new Date().toISOString(),
    })
  );
});

server.listen(port, () => {
  console.log(`${instanceName} listening on port ${port}`);
});
```

### Step 3: Add the Dockerfile

Put this in `Dockerfile`:

```Dockerfile
FROM node:22-alpine

WORKDIR /app

COPY app.js .

EXPOSE 3000

CMD ["node", "app.js"]
```

### Step 4: Add the NGINX Load Balancer Config

Put this in `nginx.conf`:

```nginx
events {}

http {
    upstream backend_pool {
        server backend1:3000;
        server backend2:3000;
    }

    server {
        listen 80;

        location / {
            proxy_pass http://backend_pool;

            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }
    }
}
```

The important part is this:

```nginx
upstream backend_pool {
    server backend1:3000;
    server backend2:3000;
}
```

That defines the group of backend servers.

This part sends traffic to that group:

```nginx
proxy_pass http://backend_pool;
```

### Step 5: Add Docker Compose

Put this in `docker-compose.yml`:

```yaml
services:
  backend1:
    build: .
    environment:
      INSTANCE_NAME: backend1

  backend2:
    build: .
    environment:
      INSTANCE_NAME: backend2

  nginx:
    image: nginx:1.27-alpine
    ports:
      - "8080:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - backend1
      - backend2
```

### Step 6: Start the System

Run:

```bash
docker compose up --build
```

You should see logs from the two backend containers and the NGINX container.

### Step 7: Send Requests Through NGINX

In another terminal:

```bash
curl http://localhost:8080
```

Run it multiple times:

```bash
for i in {1..10}; do curl -s http://localhost:8080; echo; done
```

Expected output should include both backend names:

```json
{"message":"Hello from backend","instance":"backend1","path":"/","timestamp":"..."}
```

```json
{"message":"Hello from backend","instance":"backend2","path":"/","timestamp":"..."}
```

### Step 8: Test the Health Endpoint

Run:

```bash
curl http://localhost:8080/health
```

You should receive a response from one of the backends:

```json
{"status":"ok","instance":"backend1"}
```

or:

```json
{"status":"ok","instance":"backend2"}
```

### Step 9: Simulate Backend Failure

Stop one backend:

```bash
docker compose stop backend2
```

Now send requests again:

```bash
for i in {1..10}; do curl -s http://localhost:8080; echo; done
```

You should mostly or entirely see responses from `backend1`.

Depending on timing, you may briefly see a gateway error while NGINX notices the failed backend.

### Step 10: Restore the Backend

Restart the backend:

```bash
docker compose start backend2
```

Send requests again:

```bash
for i in {1..10}; do curl -s http://localhost:8080; echo; done
```

You should see traffic distributed across both backends again.

### Step 11: Clean Up

When finished:

```bash
docker compose down
```

## Expected Outcome

After completing the exercise, you should be able to explain:

- NGINX acted as a **reverse proxy**
- The client sent requests to NGINX, not directly to the backends
- NGINX used an `upstream` block to define multiple backend servers
- Requests were distributed across `backend1` and `backend2`
- The default behavior demonstrated simple round-robin-style distribution
- When one backend stopped, traffic could still be handled by the remaining backend
- Health checks are how production load balancers decide whether a backend should receive traffic
- Sticky sessions keep a client attached to the same backend, but can make scaling and failure handling harder

You should also be comfortable drawing this:

```text
Client
  |
  v
NGINX Load Balancer
  |
  +--> backend1
  +--> backend2
```

And explaining that this pattern is used constantly in real production systems.

## Quiz Questions

1. What is the difference between a reverse proxy and a load balancer?

2. Why can sticky sessions make scaling and failure handling harder?

3. If a backend instance is running but cannot connect to the database, should it be considered ready to receive traffic? Why or why not?

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

Next, learn about **reverse proxies, API gateways, and ingress patterns** in more depth.

Load balancing answers:

```text
Which backend instance should handle this request?
```

API gateways and ingress systems add more production concerns:

```text
Which service should receive this request?
Should this request be authenticated?
Should it be rate-limited?
Should we rewrite the path?
Should we terminate TLS here?
Should we collect request metrics here?
```

A logical next topic is **API Gateways and Ingress Routing** because it builds directly on today’s load balancing foundation.
