# Day 014 — Kubernetes Pods and Deployments

Date: 2026-05-13

## Phase

Phase 2 — Containers and Platform

## Learning Objective

By the end of this lesson, you should understand how Kubernetes runs and manages application workloads using Pods and Deployments.

You should be able to explain:

- What a Pod is
- What a Deployment is
- How Kubernetes keeps the desired state running
- How reconciliation works
- How rolling updates work
- How Kubernetes self-heals failed workloads
- How to scale, update, and roll back an application Deployment

## Why This Topic Matters

In real backend and platform engineering, you rarely run a single container manually.

Instead, you usually want to say:

> “Run 3 copies of this application, keep them healthy, update them safely, and recover automatically if something fails.”

That is exactly what Kubernetes Deployments do.

Pods and Deployments are core Kubernetes workload primitives. They are used when running:

- Backend APIs
- Workers
- Frontend services
- Internal platform tools
- Microservices
- Batch-like long-running processors
- Sidecar-based workloads

If you work with Kubernetes in production, you will constantly inspect, scale, update, debug, and roll back Deployments.

## Simple Explanation

A **Pod** is the smallest thing Kubernetes runs.

Usually, one Pod contains one application container, such as:

```text
Pod
└── container: my-api
```

A **Deployment** manages Pods for you.

Instead of creating Pods directly, you usually create a Deployment and tell Kubernetes:

```text
I want 3 Pods running this application image.
```

Kubernetes then works continuously to make reality match what you asked for.

If one Pod crashes, Kubernetes creates another one.

If you change the application image, Kubernetes gradually replaces old Pods with new Pods.

If the update is bad, you can roll back to the previous version.

This is the basic idea of Kubernetes:

```text
You declare the desired state.
Kubernetes continuously reconciles the actual state toward that desired state.
```

No previous feedback contained a specific confusion to address, so this lesson focuses on the core mental model: **you describe what you want, Kubernetes keeps trying to make it true.**

## Real-World Analogy

Imagine you manage a restaurant kitchen.

You tell the shift manager:

```text
I need 3 cooks working the burger station.
```

You do not personally monitor every cook every second.

The shift manager does that.

If one cook leaves, the manager finds another cook.

If you update the recipe, the manager trains cooks one by one instead of stopping the whole kitchen.

If the new recipe is terrible, the manager goes back to the old recipe.

In this analogy:

| Real World | Kubernetes |
|---|---|
| Cook | Pod |
| Burger recipe | Container image/version |
| Shift manager | Deployment controller |
| “I need 3 cooks” | Desired replica count |
| Replacing cooks gradually | Rolling update |
| Returning to old recipe | Rollback |
| Replacing missing cooks | Self-healing |

## Technical Explanation

Kubernetes workloads are the objects that run applications.

The most important workload unit is the **Pod**.

A Pod is a wrapper around one or more containers. Containers in the same Pod share some resources, including:

- Network namespace
- Pod IP address
- Storage volumes, if configured
- Lifecycle relationship

In most beginner backend cases, a Pod contains one main application container.

Example:

```text
Pod: api-pod
├── Container: api
└── Shared network namespace
```

You usually do **not** create individual Pods manually in production.

Why?

Because if a standalone Pod dies, Kubernetes does not necessarily know that you wanted it replaced long-term.

Instead, you use a controller such as a **Deployment**.

A Deployment manages a desired number of identical Pods through lower-level objects called ReplicaSets.

The relationship looks like this:

```text
Deployment
└── ReplicaSet
    ├── Pod
    ├── Pod
    └── Pod
```

You define a Deployment like this:

```yaml
replicas: 3
image: nginx:1.25
```

That means:

```text
Desired state:
- Run 3 replicas
- Use image nginx:1.25
```

Kubernetes controllers then compare:

```text
Desired state: 3 Pods running nginx:1.25
Actual state:   2 Pods running nginx:1.25
```

Since actual state does not match desired state, Kubernetes creates another Pod.

That process is called **reconciliation**.

A Deployment supports:

### Desired State

You declare what should exist.

Example:

```text
There should be 3 replicas of my app.
```

### Reconciliation

Kubernetes repeatedly checks whether actual cluster state matches desired state.

If it does not match, Kubernetes takes action.

Example:

```text
Desired: 3 Pods
Actual: 2 Pods
Action: create 1 Pod
```

### Self-Healing

If a Pod fails, Kubernetes replaces it.

Example:

```text
Pod crashes
Deployment notices replica count is too low
New Pod is created
```

### Rolling Updates

When you change the image version, Kubernetes does not usually delete everything at once.

Instead, it gradually creates new Pods and removes old Pods.

Example:

```text
Old version: api:v1
New version: api:v2

Step 1: create one api:v2 Pod
Step 2: remove one api:v1 Pod
Step 3: repeat until all Pods run api:v2
```

### Rollbacks

If a new version is broken, you can roll back to a previous Deployment revision.

Example:

```text
api:v2 is failing
Rollback to api:v1
```

## Practical Example

Here is a simple Deployment running NGINX.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: demo-nginx
spec:
  replicas: 3
  selector:
    matchLabels:
      app: demo-nginx
  template:
    metadata:
      labels:
        app: demo-nginx
    spec:
      containers:
        - name: nginx
          image: nginx:1.25
          ports:
            - containerPort: 80
```

Important parts:

```yaml
kind: Deployment
```

This says the object is a Deployment.

```yaml
replicas: 3
```

This says Kubernetes should run 3 Pods.

```yaml
selector:
  matchLabels:
    app: demo-nginx
```

This tells the Deployment which Pods it manages.

```yaml
template:
```

This is the Pod template. It describes the Pods the Deployment should create.

```yaml
image: nginx:1.25
```

This is the container image version to run.

The mental model:

```text
Deployment spec says:
“Keep 3 Pods running from this template.”

Kubernetes says:
“I will continuously make that true.”
```

## Official Documentation To Read

- [Kubernetes — Workloads](https://kubernetes.io/docs/concepts/workloads/)
- [Kubernetes — Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)

## Good Reads

- [Kubernetes — Pods](https://kubernetes.io/docs/concepts/workloads/pods/)

## Where This Appears in Production

Pods and Deployments appear almost everywhere in Kubernetes-based production systems.

Examples:

### Backend APIs

A team may run 10 replicas of a customer API:

```text
customer-api Deployment
├── customer-api Pod
├── customer-api Pod
├── customer-api Pod
└── ...
```

If traffic increases, the team scales up replicas.

### Microservices

Each service may have its own Deployment:

```text
payments-service Deployment
orders-service Deployment
users-service Deployment
notifications-service Deployment
```

### Rolling Out New Versions

When a new application image is built in CI/CD, the platform updates the Deployment image.

Example:

```text
registry.example.com/orders-api:1.8.2
```

Kubernetes rolls out the new version gradually.

### Incident Response

If a new release causes errors, engineers may roll back:

```bash
kubectl rollout undo deployment/orders-api
```

### Self-Healing

If a node dies, Pods running on that node are rescheduled elsewhere if managed by controllers.

### Platform Operations

Platform engineers commonly inspect Deployments with:

```bash
kubectl get deployments
kubectl describe deployment <name>
kubectl get pods
kubectl rollout status deployment/<name>
```

## Common Beginner Mistakes

### 1. Creating standalone Pods directly

Beginners often create Pods directly.

That is useful for learning, but in production you usually use Deployments.

A standalone Pod is not the same as a managed, self-healing workload.

Prefer this:

```text
Deployment creates and manages Pods
```

Instead of this:

```text
Manually created Pod
```

### 2. Thinking a Pod is the same as a container

A Pod is not exactly a container.

A Pod is a Kubernetes object that can contain one or more containers.

Most simple Pods contain one container, but the concepts are not identical.

### 3. Forgetting that Deployments manage desired state

A Deployment is not just a script that runs once.

It is a declaration of desired state.

Kubernetes continuously tries to keep that state true.

### 4. Editing Pods instead of the Deployment

If a Pod is managed by a Deployment, do not manually edit the Pod expecting the change to last.

The Deployment owns the Pod template.

Change the Deployment instead.

### 5. Confusing scaling with bigger containers

Scaling replicas means running more Pods.

It does not mean giving a Pod more CPU or memory.

These are different ideas:

```text
Horizontal scaling: more Pods
Vertical scaling: more resources per Pod
```

### 6. Updating images without checking rollout status

After changing an image, always check the rollout.

Use:

```bash
kubectl rollout status deployment/<deployment-name>
```

### 7. Not knowing how to roll back

Rollback is one of the most practical Deployment skills.

You should know:

```bash
kubectl rollout undo deployment/<deployment-name>
```

### 8. Misunderstanding labels and selectors

A Deployment uses selectors to know which Pods it owns.

If labels and selectors do not match, the Deployment may not manage the Pods correctly.

Example:

```yaml
selector:
  matchLabels:
    app: demo-nginx
```

Must match:

```yaml
template:
  metadata:
    labels:
      app: demo-nginx
```

## Related Concepts

- Pods
- ReplicaSets
- Deployments
- Labels
- Selectors
- Container images
- Desired state
- Reconciliation loops
- Rolling updates
- Rollbacks
- Self-healing
- Kubernetes controllers
- Services
- Readiness probes
- Liveness probes
- Horizontal scaling
- CI/CD deployment pipelines

## Interview-Level Explanation

A Pod is the smallest deployable workload unit in Kubernetes and usually wraps one application container.

A Deployment is a higher-level controller that manages replicated Pods. You define the desired state, such as the container image and replica count, and Kubernetes continuously reconciles the actual cluster state to match it.

Deployments provide self-healing, scaling, rolling updates, and rollbacks. If a Pod crashes, the Deployment creates a replacement. If the image changes, Kubernetes gradually replaces old Pods with new ones. If the rollout is bad, the Deployment can be rolled back to a previous revision.

## Hands-On Exercise

Create a Deployment, scale replicas, update the image, and roll back.

You need a working Kubernetes environment. This can be:

- minikube
- kind
- Docker Desktop Kubernetes
- A remote development cluster

First, verify your cluster works:

```bash
kubectl get nodes
```

You should see at least one node.

### Step 1: Create a Deployment

Create a Deployment named `demo-nginx` using the `nginx:1.25` image:

```bash
kubectl create deployment demo-nginx --image=nginx:1.25
```

Check the Deployment:

```bash
kubectl get deployments
```

Check the Pods:

```bash
kubectl get pods
```

Expected idea:

```text
Deployment exists
One Pod exists
Pod eventually becomes Running
```

### Step 2: Inspect the Deployment

Run:

```bash
kubectl describe deployment demo-nginx
```

Look for:

- Name
- Replicas
- Pod template
- Image
- Conditions
- Events

Also inspect the Pods:

```bash
kubectl get pods -l app=demo-nginx
```

The `-l` flag filters by label.

### Step 3: Scale the Deployment

Scale to 3 replicas:

```bash
kubectl scale deployment demo-nginx --replicas=3
```

Check the Deployment:

```bash
kubectl get deployments
```

Check the Pods:

```bash
kubectl get pods
```

You should now see 3 Pods for `demo-nginx`.

This demonstrates desired state:

```text
Desired: 3 replicas
Kubernetes action: create enough Pods to reach 3
```

### Step 4: Delete a Pod and observe self-healing

List Pods:

```bash
kubectl get pods -l app=demo-nginx
```

Delete one Pod.

Replace `<pod-name>` with one of your actual Pod names:

```bash
kubectl delete pod <pod-name>
```

Immediately check Pods again:

```bash
kubectl get pods -l app=demo-nginx
```

You should see Kubernetes creating a replacement Pod.

This demonstrates self-healing:

```text
Desired: 3 replicas
Actual after deletion: 2 replicas
Kubernetes action: create 1 replacement Pod
```

### Step 5: Update the image

Update the Deployment image from `nginx:1.25` to `nginx:1.26`:

```bash
kubectl set image deployment/demo-nginx nginx=nginx:1.26
```

Check rollout status:

```bash
kubectl rollout status deployment/demo-nginx
```

Check Pods:

```bash
kubectl get pods -l app=demo-nginx
```

Check Deployment details:

```bash
kubectl describe deployment demo-nginx
```

This demonstrates a rolling update.

Kubernetes gradually replaces Pods using the old image with Pods using the new image.

### Step 6: View rollout history

Run:

```bash
kubectl rollout history deployment/demo-nginx
```

You should see Deployment revisions.

### Step 7: Roll back the Deployment

Roll back to the previous version:

```bash
kubectl rollout undo deployment/demo-nginx
```

Check rollout status:

```bash
kubectl rollout status deployment/demo-nginx
```

Check Deployment details:

```bash
kubectl describe deployment demo-nginx
```

You should see the Deployment return to the previous image version.

### Step 8: Export the Deployment YAML

To see the full object definition, run:

```bash
kubectl get deployment demo-nginx -o yaml
```

This output is verbose, but it helps you understand what Kubernetes stores.

Focus on:

```yaml
spec:
  replicas:
  selector:
  template:
    metadata:
      labels:
    spec:
      containers:
```

### Step 9: Clean up

Delete the Deployment:

```bash
kubectl delete deployment demo-nginx
```

Verify it is gone:

```bash
kubectl get deployments
kubectl get pods
```

## Expected Outcome

After this exercise, you should be able to explain and demonstrate:

### Desired State

You tell Kubernetes what should be true.

Example:

```text
Run 3 replicas of nginx:1.25.
```

### Reconciliation

Kubernetes compares desired state with actual state and takes action.

Example:

```text
Desired: 3 Pods
Actual: 2 Pods
Action: create 1 Pod
```

### Rolling Updates

When you update the image, Kubernetes gradually replaces old Pods with new Pods.

Example:

```text
nginx:1.25 -> nginx:1.26
```

### Self-Healing

If a Pod is deleted or crashes, Kubernetes creates a replacement because the Deployment still wants the configured number of replicas.

### Rollback

If the new version is bad, you can return to the previous revision:

```bash
kubectl rollout undo deployment/demo-nginx
```

You should also be comfortable with these commands:

```bash
kubectl create deployment
kubectl get deployments
kubectl get pods
kubectl describe deployment
kubectl scale deployment
kubectl set image
kubectl rollout status
kubectl rollout history
kubectl rollout undo
kubectl delete deployment
```

## Quiz Questions

1. What is the difference between a Pod and a Deployment?

2. If a Deployment has `replicas: 3` and one Pod is deleted, what should Kubernetes do and why?

3. What happens during a rolling update when you change a Deployment image from one version to another?

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

The next logical topic is **Kubernetes Services and networking basics**.

After you understand how Deployments create and manage Pods, the next question is:

```text
How do other applications or users reliably reach those Pods?
```

Pods can be replaced and get new IP addresses, so production systems need a stable way to route traffic to them. That is where Kubernetes Services become important.
