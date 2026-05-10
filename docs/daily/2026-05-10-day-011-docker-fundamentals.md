# Day 011 — Docker Fundamentals

Date: 2026-05-10

## Phase

Phase 2 — Containers and Platform

## Learning Objective

By the end of this lesson, you should understand the core Docker concepts used in local development and production engineering:

- What a container is
- What an image is
- How images and containers are different
- What a Dockerfile does
- How Docker uses layers
- How ports, volumes, and environment variables work
- How to build and run a small Python or Node.js application locally using Docker

## Why This Topic Matters

Docker is one of the most important tools in backend, platform, cloud, and DevOps engineering.

In real engineering teams, Docker is used to package applications so they run consistently across:

- A developer’s laptop
- CI/CD pipelines
- Staging environments
- Production servers
- Kubernetes clusters
- Cloud platforms

Without containers, teams often run into problems like:

> “It works on my machine, but not in production.”

Docker helps reduce this problem by packaging the application, its runtime, dependencies, and configuration expectations into a repeatable unit.

For backend engineers, Docker is useful because you can run services locally without installing every dependency directly on your machine.

For platform engineers, Docker is foundational because orchestration systems like Kubernetes run containers.

## Simple Explanation

A Docker image is like a packaged application template.

A Docker container is a running copy of that image.

For example:

```text
Image:      "Python app package"
Container: "The Python app currently running"
```

You create an image using a `Dockerfile`.

A `Dockerfile` is a text file that tells Docker how to build your application image.

Example instructions might be:

```text
Start with Python
Copy my app code into the image
Install dependencies
Run the application
```

Once the image is built, you can start a container from it.

```text
Dockerfile -> Image -> Container
```

A container feels like a small isolated computer process running your app, but it is not a full virtual machine. It shares the host operating system kernel and runs as an isolated process.

## Real-World Analogy

Think about baking cookies.

The `Dockerfile` is the recipe.

The Docker image is a sealed box of ready-to-bake cookie dough made from that recipe.

The Docker container is the actual batch of cookies being baked or served.

```text
Recipe       -> Dockerfile
Cookie dough -> Image
Baked cookies -> Running container
```

You can use the same image to start many containers, just like you can use the same cookie dough to bake many batches.

If you change the recipe, you need to make a new dough package. Similarly, if you change the Dockerfile or application dependencies, you rebuild the image.

## Technical Explanation

Docker packages applications into images. An image is a read-only filesystem plus metadata that describes how to run the application.

A container is a running instance of an image. It adds a writable layer on top of the image and runs a process.

### Image vs Container

```text
Image:
- Built once
- Read-only
- Contains app code, dependencies, runtime, and metadata
- Can be pushed to a registry
- Example: my-api:1.0

Container:
- Created from an image
- Running or stopped process
- Has its own filesystem layer
- Can have environment variables, mounted volumes, and port mappings
- Example: a running instance of my-api:1.0
```

### Dockerfile

A `Dockerfile` defines how to build an image.

Common Dockerfile instructions include:

```dockerfile
FROM
WORKDIR
COPY
RUN
EXPOSE
ENV
CMD
```

Example meaning:

```dockerfile
FROM python:3.12-slim
```

Start from an existing Python image.

```dockerfile
WORKDIR /app
```

Set the working directory inside the image.

```dockerfile
COPY . .
```

Copy local files into the image.

```dockerfile
RUN pip install -r requirements.txt
```

Run a command while building the image.

```dockerfile
CMD ["python", "app.py"]
```

Define the command that runs when the container starts.

### Layers

Docker images are built in layers.

Each instruction in a Dockerfile usually creates a new layer.

Example:

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

This creates layered changes:

```text
Base Python image
+ /app working directory
+ requirements.txt
+ installed Python packages
+ application source code
+ default startup command
```

Layers matter because Docker can cache them.

If your dependencies do not change, Docker can reuse the previous dependency layer instead of reinstalling everything.

That is why this pattern is common:

```dockerfile
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
```

Instead of copying everything first.

### Ports

Containers have their own network namespace. If an app listens on port `8000` inside the container, that does not automatically expose it on your laptop.

You need a port mapping:

```bash
docker run -p 8000:8000 my-python-app
```

This means:

```text
host port 8000 -> container port 8000
```

If the app listens on port `8000` inside the container, you can access it from your laptop at:

```text
http://localhost:8000
```

### Volumes

A container filesystem is temporary by default.

If a container writes files and then gets deleted, those files are usually gone.

Volumes are used to persist data or mount local files into containers.

Example:

```bash
docker run -v "$PWD:/app" my-python-app
```

This mounts your current local directory into `/app` inside the container.

Volumes are commonly used for:

- Local development
- Databases
- Logs
- Persistent application data
- Sharing files between host and container

### Environment Variables

Environment variables are used to pass configuration into containers.

Example:

```bash
docker run -e APP_ENV=development my-python-app
```

Inside the container, the app can read:

```text
APP_ENV=development
```

This is commonly used for:

- App environment
- Database URLs
- API keys
- Feature flags
- Service configuration

Important: environment variables are useful, but secrets should be handled carefully in production.

## Practical Example

Here is a small Python web app using Flask.

Project structure:

```text
docker-python-demo/
├── app.py
├── requirements.txt
└── Dockerfile
```

Create `app.py`:

```python
import os
from flask import Flask

app = Flask(__name__)

@app.get("/")
def home():
    app_env = os.getenv("APP_ENV", "local")
    return {
        "message": "Hello from Docker",
        "environment": app_env
    }

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
```

Create `requirements.txt`:

```txt
flask==3.0.3
```

Create `Dockerfile`:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

ENV APP_ENV=local

CMD ["python", "app.py"]
```

Build the image:

```bash
docker build -t docker-python-demo:1.0 .
```

Run the container:

```bash
docker run --name demo-app -p 8000:8000 -e APP_ENV=development docker-python-demo:1.0
```

Test it:

```bash
curl http://localhost:8000
```

Expected response:

```json
{
  "environment": "development",
  "message": "Hello from Docker"
}
```

Stop the container:

```bash
docker stop demo-app
```

Remove the container:

```bash
docker rm demo-app
```

Run it again with a different environment variable:

```bash
docker run --name demo-app-prod -p 8000:8000 -e APP_ENV=production docker-python-demo:1.0
```

Test again:

```bash
curl http://localhost:8000
```

You should see:

```json
{
  "environment": "production",
  "message": "Hello from Docker"
}
```

This shows that the same image can run with different runtime configuration.

## Official Documentation To Read

- [Docker Docs — Get started](https://docs.docker.com/get-started/)
- [Docker Docs](https://docs.docker.com/)

## Good Reads

- [Docker — Manuals](https://docs.docker.com/manuals/)

## Where This Appears in Production

Docker appears in many production systems.

### Backend Services

A backend API may be packaged as a Docker image:

```text
api-service:1.24.0
```

That image can be deployed to staging and production.

### CI/CD Pipelines

A pipeline may:

```text
1. Run tests
2. Build a Docker image
3. Tag the image
4. Push it to a registry
5. Deploy it to a runtime platform
```

Example image tags:

```text
payments-api:latest
payments-api:1.8.3
payments-api:git-sha-a91f3c2
```

### Kubernetes

Kubernetes does not usually run your raw source code directly.

It runs containers.

A Kubernetes Pod references a container image:

```text
image: payments-api:1.8.3
```

### Local Development

Developers often use Docker to run local dependencies:

```text
PostgreSQL
Redis
Kafka
Elasticsearch
LocalStack
```

This avoids installing everything directly on the host machine.

### Platform Engineering

Platform teams create base images, build pipelines, container standards, and deployment systems.

They care about:

- Image size
- Security scanning
- Reproducible builds
- Runtime configuration
- Logging
- Networking
- Resource limits
- Deployment safety

## Common Beginner Mistakes

### 1. Confusing an image with a container

An image is the packaged template.

A container is a running or stopped instance of that image.

```text
Image -> can create many containers
```

### 2. Thinking containers are full virtual machines

Containers are isolated, but they are not full VMs.

They share the host operating system kernel.

This makes them lighter and faster than VMs, but also means they behave differently.

### 3. Forgetting to map ports

If your app listens on port `8000` inside the container, you still need:

```bash
-p 8000:8000
```

Without this, you may not be able to access it from your host machine.

### 4. Binding to `localhost` inside the container

If your app binds to `127.0.0.1` inside the container, it may only listen inside the container.

For web apps, bind to:

```text
0.0.0.0
```

Example:

```python
app.run(host="0.0.0.0", port=8000)
```

### 5. Rebuilding more than necessary

This is less efficient:

```dockerfile
COPY . .
RUN pip install -r requirements.txt
```

If any source file changes, Docker may reinstall dependencies.

This is usually better:

```dockerfile
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
```

### 6. Putting secrets directly into images

Avoid putting secrets into a Dockerfile:

```dockerfile
ENV API_KEY=real-secret-value
```

That secret can become part of the image history or be exposed to other users.

Pass sensitive configuration securely at runtime instead.

### 7. Assuming container data always persists

If you write data inside a container and delete the container, that data can disappear.

Use volumes for persistent data.

### 8. Using `latest` everywhere

The `latest` tag can change over time.

This can make builds and deployments unpredictable.

Prefer versioned tags when possible:

```text
python:3.12-slim
my-api:1.0.0
```

### 9. Building very large images

Large images are slower to build, push, pull, scan, and deploy.

Use smaller base images when appropriate.

Example:

```dockerfile
FROM python:3.12-slim
```

Instead of a larger general-purpose image.

### 10. Not checking logs

When a container fails, check logs:

```bash
docker logs <container-name>
```

Example:

```bash
docker logs demo-app
```

## Related Concepts

- Container images
- Container runtimes
- Dockerfile
- Image layers
- Build cache
- Port mapping
- Volumes
- Bind mounts
- Environment variables
- Docker Compose
- Container registries
- CI/CD pipelines
- Kubernetes Pods
- Service deployment
- Runtime configuration
- Immutable infrastructure
- Observability in containers
- Container security scanning

## Interview-Level Explanation

Docker packages an application and its dependencies into an image. An image is a read-only template built from a Dockerfile. A container is a running instance of that image with its own isolated filesystem, process space, and network configuration.

Docker images are built in layers, which improves caching and makes builds more efficient. At runtime, containers can be configured with port mappings, environment variables, and volumes. Ports expose container services to the host, environment variables provide runtime configuration, and volumes persist or share data.

Docker is commonly used to make development, CI/CD, and production deployments more consistent across environments.

## Hands-On Exercise

Write a Dockerfile for a small Python or Node.js app and run it locally.

You can choose Python or Node.js. The Python version is shown below.

### Option A: Python Flask App

#### Step 1: Create a project directory

```bash
mkdir docker-python-demo
cd docker-python-demo
```

#### Step 2: Create `app.py`

```bash
touch app.py
```

Add this code:

```python
import os
from flask import Flask

app = Flask(__name__)

@app.get("/")
def home():
    return {
        "message": "Hello from a Docker container",
        "app_env": os.getenv("APP_ENV", "local")
    }

@app.get("/health")
def health():
    return {
        "status": "ok"
    }

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
```

#### Step 3: Create `requirements.txt`

```bash
touch requirements.txt
```

Add:

```txt
flask==3.0.3
```

#### Step 4: Create `Dockerfile`

```bash
touch Dockerfile
```

Add:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

ENV APP_ENV=local

CMD ["python", "app.py"]
```

#### Step 5: Build the Docker image

```bash
docker build -t docker-python-demo:1.0 .
```

Check that the image exists:

```bash
docker images
```

You should see something like:

```text
REPOSITORY           TAG       IMAGE ID       CREATED          SIZE
docker-python-demo   1.0       abc123...      few seconds ago  ...
```

#### Step 6: Run the container

```bash
docker run --name docker-python-demo-container -p 8000:8000 -e APP_ENV=development docker-python-demo:1.0
```

This command means:

```text
--name docker-python-demo-container
Give the container a readable name.

-p 8000:8000
Map host port 8000 to container port 8000.

-e APP_ENV=development
Pass an environment variable into the container.

docker-python-demo:1.0
Use this image to create the container.
```

#### Step 7: Test the app

In another terminal, run:

```bash
curl http://localhost:8000
```

Expected response:

```json
{
  "app_env": "development",
  "message": "Hello from a Docker container"
}
```

Test the health endpoint:

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{
  "status": "ok"
}
```

#### Step 8: View running containers

```bash
docker ps
```

You should see your running container.

#### Step 9: View logs

```bash
docker logs docker-python-demo-container
```

#### Step 10: Stop the container

```bash
docker stop docker-python-demo-container
```

#### Step 11: Remove the stopped container

```bash
docker rm docker-python-demo-container
```

#### Step 12: Run the same image with a different environment

```bash
docker run --name docker-python-demo-prod -p 8000:8000 -e APP_ENV=production docker-python-demo:1.0
```

Test it:

```bash
curl http://localhost:8000
```

You should now see:

```json
{
  "app_env": "production",
  "message": "Hello from a Docker container"
}
```

This proves the same image can run with different runtime configuration.

#### Step 13: Stop and remove the second container

```bash
docker stop docker-python-demo-prod
docker rm docker-python-demo-prod
```

### Option B: Node.js Express App

If you prefer Node.js, use this version.

#### Step 1: Create a project directory

```bash
mkdir docker-node-demo
cd docker-node-demo
```

#### Step 2: Create `package.json`

```json
{
  "name": "docker-node-demo",
  "version": "1.0.0",
  "main": "server.js",
  "scripts": {
    "start": "node server.js"
  },
  "dependencies": {
    "express": "4.19.2"
  }
}
```

#### Step 3: Create `server.js`

```javascript
const express = require("express");

const app = express();
const port = 8000;

app.get("/", (req, res) => {
  res.json({
    message: "Hello from a Docker container",
    app_env: process.env.APP_ENV || "local"
  });
});

app.get("/health", (req, res) => {
  res.json({
    status: "ok"
  });
});

app.listen(port, "0.0.0.0", () => {
  console.log(`App listening on port ${port}`);
});
```

#### Step 4: Create `Dockerfile`

```dockerfile
FROM node:20-slim

WORKDIR /app

COPY package.json package-lock.json* ./

RUN npm install

COPY . .

EXPOSE 8000

ENV APP_ENV=local

CMD ["npm", "start"]
```

#### Step 5: Build the image

```bash
docker build -t docker-node-demo:1.0 .
```

#### Step 6: Run the container

```bash
docker run --name docker-node-demo-container -p 8000:8000 -e APP_ENV=development docker-node-demo:1.0
```

#### Step 7: Test it

```bash
curl http://localhost:8000
```

Expected response:

```json
{
  "message": "Hello from a Docker container",
  "app_env": "development"
}
```

#### Step 8: Stop and remove it

```bash
docker stop docker-node-demo-container
docker rm docker-node-demo-container
```

### Optional: Try a Volume for Local Development

For Python:

```bash
docker run --name docker-python-demo-dev \
  -p 8000:8000 \
  -e APP_ENV=development \
  -v "$PWD:/app" \
  docker-python-demo:1.0
```

This mounts your current directory into `/app` inside the container.

If you edit local files, the container can see those files. Depending on the framework and server setup, you may still need to restart the process to see changes.

Clean up:

```bash
docker stop docker-python-demo-dev
docker rm docker-python-demo-dev
```

## Expected Outcome

After this exercise, you should be able to explain and demonstrate:

- The difference between an image and a container
- How a Dockerfile builds an image
- Why Dockerfile instruction order matters for caching
- What image layers are
- How to build an image with `docker build`
- How to run a container with `docker run`
- How to expose container ports with `-p`
- How to pass configuration with environment variables using `-e`
- How to use a volume or bind mount with `-v`
- How to inspect running containers with `docker ps`
- How to check container logs with `docker logs`
- How to stop and remove containers

You should be comfortable saying:

> I can package a small backend app into a Docker image and run it locally as a container with ports and environment variables configured.

## Quiz Questions

1. What is the difference between a Docker image and a Docker container?

2. Why is this Dockerfile pattern usually better?

   ```dockerfile
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   ```

   Compared to this?

   ```dockerfile
   COPY . .
   RUN pip install -r requirements.txt
   ```

3. If an application listens on port `8000` inside a container, what does this command do?

   ```bash
   docker run -p 3000:8000 my-app
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

The next logical topic is Docker Compose.

Once you understand a single container, the next step is learning how to run multiple containers together, such as:

```text
backend API + PostgreSQL + Redis
```

Docker Compose helps define and run multi-container local development environments using a YAML file.
