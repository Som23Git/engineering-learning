# Day 012 — Docker Compose

Date: 2026-05-11

## Phase

Phase 2 — Containers and Platform

## Learning Objective

By the end of this lesson, you should understand how to run a local multi-container application using Docker Compose.

You should be able to explain:

- What a Compose `service` is
- How containers communicate using a Compose network
- Why volumes are used for persistent data
- How environment variables configure containers
- How a local app depends on services like PostgreSQL

## Why This Topic Matters

Most real backend applications do not run alone.

A typical backend service often needs:

- A database, such as PostgreSQL
- A cache, such as Redis
- A message broker, such as RabbitMQ or Kafka
- A local object store
- A background worker
- Observability tools

Starting all of these manually is slow and error-prone.

Docker Compose solves this problem for local development by letting you define a multi-container environment in one file: `docker-compose.yml` or `compose.yml`.

In real engineering teams, Docker Compose is commonly used to:

- Run local development environments
- Share setup instructions across teams
- Test service dependencies locally
- Reproduce bugs in a controlled environment
- Create lightweight integration test environments

It is not usually the final production orchestrator for large systems, but the concepts prepare you for Kubernetes and other platform tools.

## Simple Explanation

Docker runs one container from one image.

Docker Compose runs multiple related containers together.

For example, your backend app may need a PostgreSQL database. Instead of starting the app and database separately, you describe both in a Compose file.

Docker Compose then starts them together.

Example:

```text
Your laptop
└── Docker Compose project
    ├── app container
    └── postgres container
```

The app container can talk to the PostgreSQL container by using the database service name, such as:

```text
postgres
```

not:

```text
localhost
```

This is an important beginner point.

Inside a container, `localhost` means “this same container,” not your whole laptop and not another container.

## Real-World Analogy

Imagine a small restaurant.

The restaurant needs several roles to operate:

- Chef
- Cashier
- Dishwasher
- Supplier

You could call each person manually every morning and explain what to do.

Or you could have one daily startup checklist:

```text
1. Chef arrives at 8:00
2. Cashier arrives at 8:30
3. Dishwasher starts after breakfast setup
4. Supplier delivers ingredients
```

Docker Compose is like that startup checklist for containers.

It does not just start one thing. It starts a group of related things with the right configuration.

## Technical Explanation

Docker Compose uses a YAML file to define an application made of multiple services.

A **service** is usually one container role.

For example:

```yaml
services:
  app:
    build: .
  postgres:
    image: postgres:16
```

This defines two services:

- `app`
- `postgres`

Each service becomes one or more containers.

Compose automatically creates a default network for the project. Containers on that network can reach each other by service name.

So if your app needs to connect to PostgreSQL, the hostname is:

```text
postgres
```

because that is the service name.

A Compose file commonly defines:

### Services

Services are the containers that make up the app.

Example:

```yaml
services:
  app:
    build: .
  postgres:
    image: postgres:16
```

### Networks

Networks let containers communicate.

Compose creates a default network automatically, but you can also define your own.

Example:

```yaml
networks:
  app-network:
```

### Volumes

Volumes persist data beyond the life of a container.

This matters for databases.

Without a volume, deleting the PostgreSQL container can delete the database files.

Example:

```yaml
volumes:
  postgres-data:
```

### Environment Variables

Environment variables configure containers without hardcoding values into the image.

Example:

```yaml
environment:
  POSTGRES_DB: appdb
  POSTGRES_USER: appuser
  POSTGRES_PASSWORD: apppassword
```

### Dependencies

Services often depend on other services.

Your app depends on PostgreSQL being available.

Compose can express startup order using `depends_on`:

```yaml
depends_on:
  - postgres
```

Important: `depends_on` controls startup order, but it does not always mean the database is fully ready to accept connections. Real apps should retry database connections during startup.

## Practical Example

Here is a simple local backend application with PostgreSQL.

Architecture:

```text
Browser / curl
     |
     v
localhost:3000
     |
     v
app container
     |
     v
postgres container
```

Project structure:

```text
compose-demo/
├── compose.yml
├── Dockerfile
├── package.json
└── server.js
```

### `compose.yml`

```yaml
services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      DATABASE_HOST: postgres
      DATABASE_PORT: 5432
      DATABASE_NAME: appdb
      DATABASE_USER: appuser
      DATABASE_PASSWORD: apppassword
    depends_on:
      - postgres

  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: appdb
      POSTGRES_USER: appuser
      POSTGRES_PASSWORD: apppassword
    volumes:
      - postgres-data:/var/lib/postgresql/data

volumes:
  postgres-data:
```

### `Dockerfile`

```dockerfile
FROM node:22-alpine

WORKDIR /app

COPY package.json package.json
RUN npm install

COPY server.js server.js

EXPOSE 3000

CMD ["node", "server.js"]
```

### `package.json`

```json
{
  "name": "compose-demo",
  "version": "1.0.0",
  "main": "server.js",
  "scripts": {
    "start": "node server.js"
  },
  "dependencies": {
    "pg": "^8.13.0"
  }
}
```

### `server.js`

```javascript
const http = require("http");
const { Client } = require("pg");

const port = 3000;

const dbConfig = {
  host: process.env.DATABASE_HOST,
  port: Number(process.env.DATABASE_PORT),
  database: process.env.DATABASE_NAME,
  user: process.env.DATABASE_USER,
  password: process.env.DATABASE_PASSWORD,
};

async function checkDatabase() {
  const client = new Client(dbConfig);

  try {
    await client.connect();
    const result = await client.query("SELECT NOW() as current_time");
    await client.end();

    return {
      ok: true,
      time: result.rows[0].current_time,
    };
  } catch (error) {
    return {
      ok: false,
      error: error.message,
    };
  }
}

const server = http.createServer(async (req, res) => {
  if (req.url === "/health") {
    const db = await checkDatabase();

    res.writeHead(db.ok ? 200 : 500, {
      "Content-Type": "application/json",
    });

    res.end(
      JSON.stringify({
        app: "ok",
        database: db,
      })
    );

    return;
  }

  res.writeHead(200, {
    "Content-Type": "text/plain",
  });

  res.end("Docker Compose app is running\n");
});

server.listen(port, () => {
  console.log(`Server listening on port ${port}`);
});
```

Run it:

```bash
docker compose up --build
```

In another terminal:

```bash
curl http://localhost:3000
```

Expected response:

```text
Docker Compose app is running
```

Check database connectivity:

```bash
curl http://localhost:3000/health
```

Expected response shape:

```json
{
  "app": "ok",
  "database": {
    "ok": true,
    "time": "2026-05-11T..."
  }
}
```

Stop the environment:

```bash
docker compose down
```

Stop and remove the database volume too:

```bash
docker compose down -v
```

Be careful with `-v`. It removes persisted database data.

## Official Documentation To Read

- [Docker Compose Documentation](https://docs.docker.com/compose/)

## Good Reads

- [Docker Docs — Guides](https://docs.docker.com/guides/)

## Where This Appears in Production

Docker Compose itself is most common in local development and smaller environments.

You will see Compose used for:

- Local backend development
- Local database and cache setup
- Integration testing
- Demo environments
- Developer onboarding
- Reproducing production-like bugs locally

The ideas behind Docker Compose appear in production platforms too.

For example:

| Docker Compose Concept | Production Equivalent |
|---|---|
| Service | Kubernetes Deployment, ECS Service, Nomad job |
| Container image | Same container image used in production |
| Environment variables | ConfigMaps, Secrets, task environment |
| Volume | PersistentVolume, cloud disk, database storage |
| Network | Kubernetes Service, cloud VPC, service mesh |
| Health check | Readiness/liveness probes, load balancer checks |

Compose helps you understand the basic building blocks before learning larger orchestrators.

## Common Beginner Mistakes

### 1. Using `localhost` incorrectly

Inside the app container, this is usually wrong:

```text
localhost:5432
```

That means the app container is trying to find PostgreSQL inside itself.

Use the Compose service name instead:

```text
postgres:5432
```

### 2. Forgetting that containers are isolated

Each container has its own filesystem, process space, and network view.

Your app container and database container are separate machines from the application’s perspective.

### 3. Not using a volume for database data

If PostgreSQL stores data only inside the container, removing the container can remove the data.

Use a named volume:

```yaml
volumes:
  - postgres-data:/var/lib/postgresql/data
```

### 4. Thinking `depends_on` means “ready”

This:

```yaml
depends_on:
  - postgres
```

means Compose starts `postgres` before `app`.

It does not guarantee PostgreSQL is ready to accept connections.

Your app should handle retries or expose a startup failure clearly.

### 5. Hardcoding secrets into code

Do not put database passwords directly into application source code.

For local development, environment variables in Compose are acceptable for learning.

For real systems, secrets should be handled more carefully.

### 6. Confusing image build and container start

This builds the app image and starts containers:

```bash
docker compose up --build
```

This starts containers without forcing a rebuild:

```bash
docker compose up
```

If you changed the Dockerfile or dependencies, you may need `--build`.

### 7. Forgetting to clean up

After experiments, containers and volumes can remain on your machine.

Useful commands:

```bash
docker compose down
```

```bash
docker compose down -v
```

Again, `-v` removes volumes and can delete local database data.

## Related Concepts

- Docker images
- Docker containers
- Container networking
- Port mapping
- Environment variables
- Volumes and persistent storage
- Service discovery
- Local development environments
- Database connection strings
- Health checks
- Dependency startup order
- Kubernetes Pods and Services
- Platform engineering developer experience

## Interview-Level Explanation

Docker Compose is a tool for defining and running multi-container applications locally. A Compose file describes services such as an app, database, cache, or worker. Compose creates a network so services can communicate by service name, supports volumes for persistent data, and uses environment variables for configuration. It is commonly used for local development and integration testing, while production systems often use orchestrators like Kubernetes or managed container platforms.

## Hands-On Exercise

Use Docker Compose to run an app and PostgreSQL locally.

### Step 1: Create a project directory

```bash
mkdir compose-demo
cd compose-demo
```

### Step 2: Create `compose.yml`

```bash
touch compose.yml
```

Paste this:

```yaml
services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      DATABASE_HOST: postgres
      DATABASE_PORT: 5432
      DATABASE_NAME: appdb
      DATABASE_USER: appuser
      DATABASE_PASSWORD: apppassword
    depends_on:
      - postgres

  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: appdb
      POSTGRES_USER: appuser
      POSTGRES_PASSWORD: apppassword
    volumes:
      - postgres-data:/var/lib/postgresql/data

volumes:
  postgres-data:
```

### Step 3: Create `Dockerfile`

```bash
touch Dockerfile
```

Paste this:

```dockerfile
FROM node:22-alpine

WORKDIR /app

COPY package.json package.json
RUN npm install

COPY server.js server.js

EXPOSE 3000

CMD ["node", "server.js"]
```

### Step 4: Create `package.json`

```bash
touch package.json
```

Paste this:

```json
{
  "name": "compose-demo",
  "version": "1.0.0",
  "main": "server.js",
  "scripts": {
    "start": "node server.js"
  },
  "dependencies": {
    "pg": "^8.13.0"
  }
}
```

### Step 5: Create `server.js`

```bash
touch server.js
```

Paste this:

```javascript
const http = require("http");
const { Client } = require("pg");

const port = 3000;

const dbConfig = {
  host: process.env.DATABASE_HOST,
  port: Number(process.env.DATABASE_PORT),
  database: process.env.DATABASE_NAME,
  user: process.env.DATABASE_USER,
  password: process.env.DATABASE_PASSWORD,
};

async function checkDatabase() {
  const client = new Client(dbConfig);

  try {
    await client.connect();
    const result = await client.query("SELECT NOW() as current_time");
    await client.end();

    return {
      ok: true,
      time: result.rows[0].current_time,
    };
  } catch (error) {
    return {
      ok: false,
      error: error.message,
    };
  }
}

const server = http.createServer(async (req, res) => {
  if (req.url === "/health") {
    const db = await checkDatabase();

    res.writeHead(db.ok ? 200 : 500, {
      "Content-Type": "application/json",
    });

    res.end(
      JSON.stringify({
        app: "ok",
        database: db,
      })
    );

    return;
  }

  res.writeHead(200, {
    "Content-Type": "text/plain",
  });

  res.end("Docker Compose app is running\n");
});

server.listen(port, () => {
  console.log(`Server listening on port ${port}`);
});
```

### Step 6: Start the application

```bash
docker compose up --build
```

Watch the logs.

You should see logs for both services:

```text
app
postgres
```

### Step 7: Test the app

Open a second terminal from the same project directory.

Run:

```bash
curl http://localhost:3000
```

Expected:

```text
Docker Compose app is running
```

Now test the database connection:

```bash
curl http://localhost:3000/health
```

Expected response should show:

```json
{
  "app": "ok",
  "database": {
    "ok": true
  }
}
```

The timestamp may differ.

### Step 8: Inspect running containers

```bash
docker compose ps
```

You should see both services running.

### Step 9: View logs

```bash
docker compose logs
```

View logs for only the app:

```bash
docker compose logs app
```

View logs for only PostgreSQL:

```bash
docker compose logs postgres
```

### Step 10: Stop the environment

```bash
docker compose down
```

### Step 11: Confirm data volume behavior

Start it again:

```bash
docker compose up
```

PostgreSQL should reuse the named volume:

```text
postgres-data
```

Now stop and delete the volume:

```bash
docker compose down -v
```

This removes the local database data.

## Expected Outcome

After completing the exercise, you should be able to:

- Run a backend app and PostgreSQL together using Docker Compose
- Explain that each top-level item under `services` defines a service
- Explain that Compose creates a network where services can reach each other by name
- Explain why the app uses `DATABASE_HOST=postgres` instead of `localhost`
- Explain how `ports` exposes the app from the container to your laptop
- Explain how environment variables configure the app and database
- Explain why PostgreSQL needs a volume for persistent local data
- Use basic Compose commands:
  - `docker compose up`
  - `docker compose up --build`
  - `docker compose ps`
  - `docker compose logs`
  - `docker compose down`
  - `docker compose down -v`

## Quiz Questions

1. In a Docker Compose project, why should the app connect to PostgreSQL using `postgres` as the hostname instead of `localhost`?

2. What problem does a named volume solve for a PostgreSQL container?

3. What is the difference between `docker compose down` and `docker compose down -v`?

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

Next, learn about container networking and how services communicate across container boundaries. This will deepen your understanding of what Docker Compose is doing automatically when it lets the app container reach the PostgreSQL container by service name.
