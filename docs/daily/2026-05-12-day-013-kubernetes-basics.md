# Day 013 — Kubernetes Basics

Date: 2026-05-12

## Phase

Phase 2 — Containers and Platform

## Learning Objective

By the end of this lesson, you should understand what Kubernetes does, why engineering teams use it, and how the basic building blocks fit together:

- Pods
- Deployments
- ReplicaSets
- Services
- Basic cluster architecture

You should also be able to run a simple application in Kubernetes using `minikube` or `kind`, then expose it through a Service.

## Why This Topic Matters

In real backend and platform engineering, applications rarely run as one manually started process on one server.

Production systems usually need:

- Multiple copies of an application for reliability
- Automatic restarts when containers crash
- Safe rolling updates
- Network access between services
- Load balancing across application instances
- Declarative infrastructure
- A consistent way to run workloads across machines

Docker lets you package and run a container.

Kubernetes helps you run many containers reliably across a cluster of machines.

This matters because modern backend systems are often deployed onto Kubernetes or Kubernetes-like platforms. Even if you do not manage Kubernetes directly, understanding its core model helps you understand how production applications are scheduled, restarted, exposed, scaled, and updated.

## Simple Explanation

Kubernetes is a system for running containers.

Instead of manually doing this:

```bash
docker run my-api
docker run my-api
docker run my-api
```

And then manually restarting containers when they crash, manually deciding which machine should run them, and manually exposing them to users, you tell Kubernetes what you want:

> “Run 3 copies of this application and keep them running.”

Kubernetes then works to make the real world match your desired state.

For example, if you say:

> “I want 3 replicas of my web app.”

Kubernetes checks the cluster:

- Are 3 copies running?
- Did one crash?
- Is a node full?
- Does a replacement need to be created?
- Should traffic be sent to the healthy copies?

Kubernetes is not just a container runner. It is a control system for containerized applications.

## Real-World Analogy

Think of Kubernetes like a restaurant manager.

You, the application owner, say:

> “I need 3 cooks working the burger station.”

The manager does not just hear the request once and walk away. The manager keeps checking:

- Are 3 cooks still working?
- Did one leave?
- Is one station broken?
- Do we need to move someone to another station?
- Are orders being routed to available cooks?

In this analogy:

| Kubernetes Concept | Restaurant Analogy |
|---|---|
| Container | A cook doing one specific job |
| Pod | A workstation where one or more cooks work together |
| Deployment | The instruction: “Keep 3 burger stations running” |
| ReplicaSet | The mechanism that maintains the correct number of stations |
| Service | The order counter that sends work to available stations |
| Node | A kitchen |
| Cluster | All kitchens managed together |
| Control plane | The restaurant management office |

The important idea: Kubernetes constantly reconciles desired state with actual state.

## Technical Explanation

Kubernetes is an orchestration platform for containerized workloads.

You describe the desired state of your application using Kubernetes objects, usually written in YAML. Kubernetes controllers then work continuously to make the actual cluster state match that desired state.

### Basic Cluster Architecture

A Kubernetes cluster has two main parts:

```text
Kubernetes Cluster
├── Control Plane
│   ├── API Server
│   ├── Scheduler
│   ├── Controller Manager
│   └── etcd
│
└── Worker Nodes
    ├── kubelet
    ├── container runtime
    └── Pods
```

### Control Plane

The control plane manages the cluster.

Important components:

| Component | Purpose |
|---|---|
| API Server | Main entry point for Kubernetes commands and API requests |
| etcd | Stores cluster state |
| Scheduler | Decides which node should run a new Pod |
| Controller Manager | Runs controllers that reconcile desired state with actual state |

When you run:

```bash
kubectl apply -f deployment.yaml
```

You are sending a request to the Kubernetes API server.

### Worker Nodes

Worker nodes are the machines where your application containers actually run.

Each worker node usually has:

| Component | Purpose |
|---|---|
| kubelet | Agent that communicates with the control plane and manages Pods on the node |
| container runtime | Runs containers, such as containerd |
| Pods | The smallest deployable units in Kubernetes |

### Pod

A Pod is the smallest unit Kubernetes schedules.

A Pod usually contains one container, but it can contain multiple tightly related containers that need to share:

- Network namespace
- Storage volumes
- Lifecycle

Example:

```text
Pod
└── Container: nginx
```

Important: Kubernetes does not usually run standalone containers directly. It runs Pods.

### Deployment

A Deployment manages application rollout and updates.

You usually create a Deployment instead of creating Pods manually.

A Deployment says something like:

> “Run 3 replicas of this application using this container image.”

Example responsibilities:

- Create Pods
- Replace failed Pods
- Support rolling updates
- Roll back to previous versions
- Maintain desired replica count indirectly through ReplicaSets

### ReplicaSet

A ReplicaSet ensures that a specified number of Pod replicas are running.

Usually, you do not create ReplicaSets directly. A Deployment creates and manages them for you.

Relationship:

```text
Deployment
└── ReplicaSet
    ├── Pod
    ├── Pod
    └── Pod
```

If one Pod crashes or is deleted, the ReplicaSet creates another one.

### Service

Pods are temporary. They can be created, destroyed, replaced, and rescheduled.

That creates a problem:

> If Pods keep changing, how does another application reliably talk to them?

A Service provides a stable network endpoint for a group of Pods.

The Service selects Pods using labels.

Example:

```text
Service: my-web-service
        |
        | selects Pods with label app=web
        |
        v
    ┌────────┬────────┬────────┐
    │ Pod 1  │ Pod 2  │ Pod 3  │
    └────────┴────────┴────────┘
```

The Service gives clients one stable address, while Kubernetes routes traffic to the matching healthy Pods.

## Practical Example

Here is a basic Deployment and Service for an NGINX web server.

Create a file named `nginx-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-demo
spec:
  replicas: 2
  selector:
    matchLabels:
      app: nginx-demo
  template:
    metadata:
      labels:
        app: nginx-demo
    spec:
      containers:
        - name: nginx
          image: nginx:1.27
          ports:
            - containerPort: 80
```

Create a file named `nginx-service.yaml`:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-demo-service
spec:
  type: NodePort
  selector:
    app: nginx-demo
  ports:
    - port: 80
      targetPort: 80
      nodePort: 30080
```

Apply them:

```bash
kubectl apply -f nginx-deployment.yaml
kubectl apply -f nginx-service.yaml
```

Check the Deployment:

```bash
kubectl get deployments
```

Check the Pods:

```bash
kubectl get pods
```

Check the Service:

```bash
kubectl get services
```

You should see something like:

```text
NAME                 TYPE       CLUSTER-IP      EXTERNAL-IP   PORT(S)
nginx-demo-service   NodePort   10.x.x.x        <none>        80:30080/TCP
```

If using `minikube`, you can open the Service with:

```bash
minikube service nginx-demo-service
```

Or get the URL:

```bash
minikube service nginx-demo-service --url
```

Then test it:

```bash
curl <URL_FROM_MINIKUBE>
```

If using `kind`, NodePort access depends on how your kind cluster is configured. For a beginner exercise, `minikube` is usually simpler for testing Services from your local machine.

## Official Documentation To Read

- [Kubernetes — Concepts](https://kubernetes.io/docs/concepts/)
- [Kubernetes — Learn Kubernetes Basics](https://kubernetes.io/docs/tutorials/kubernetes-basics/)

## Good Reads

- [Kubernetes — Glossary](https://kubernetes.io/docs/reference/glossary/)

## Where This Appears in Production

Kubernetes appears in many production environments as the platform where backend services run.

Common production examples:

### Backend APIs

A backend team may run an API as a Kubernetes Deployment:

```text
api-service Deployment
├── api-service Pod
├── api-service Pod
└── api-service Pod
```

A Service exposes those Pods internally so other applications can call it.

### Microservices

In a microservice architecture, each service may have its own Deployment and Service:

```text
users-service
orders-service
payments-service
notifications-service
```

Each one can scale independently.

### Internal Platforms

Platform teams often build deployment systems on top of Kubernetes.

Developers may not write raw Kubernetes YAML every day, but their code may still end up running as:

- Deployments
- Pods
- Services
- ConfigMaps
- Secrets
- Ingress resources

### CI/CD Deployments

A CI/CD pipeline may build a Docker image, push it to a registry, and update a Kubernetes Deployment:

```text
Code commit
  -> Build image
  -> Push image
  -> Update Kubernetes Deployment
  -> Rolling update starts
```

### Reliability and Self-Healing

If a container crashes, Kubernetes can restart it.

If a node fails, Kubernetes can reschedule Pods onto other nodes, depending on the workload and cluster capacity.

This is one reason teams use Kubernetes: it helps automate operational recovery.

## Common Beginner Mistakes

### 1. Thinking Kubernetes replaces Docker

Kubernetes does not replace containers. It orchestrates containers.

Docker is commonly used for building and running containers locally. Kubernetes runs containerized workloads in a cluster using a container runtime.

### 2. Thinking a Pod is the same as a container

A Pod is a Kubernetes object that contains one or more containers.

Most beginner examples use one container per Pod, but they are not the same thing.

### 3. Creating Pods directly in production

You usually do not create standalone Pods directly.

Instead, use higher-level objects like Deployments, because they can recreate Pods, manage replicas, and perform updates.

### 4. Not understanding labels and selectors

Services find Pods using labels and selectors.

If the labels do not match, the Service will not send traffic to your Pods.

Example mismatch:

```yaml
# Pod label
app: nginx-demo

# Service selector
app: nginx
```

This Service would not select the Pods.

### 5. Forgetting that Pods are temporary

Pods can be deleted and recreated at any time.

Do not rely on a single Pod’s IP address as a stable endpoint. Use a Service.

### 6. Confusing Deployment and ReplicaSet

A Deployment manages ReplicaSets.

A ReplicaSet manages Pods.

Usually, you interact with the Deployment.

### 7. Assuming Kubernetes automatically makes bad applications reliable

Kubernetes can restart failed containers and reschedule workloads, but your application still needs good engineering:

- Health checks
- Timeouts
- Graceful shutdown
- Externalized state
- Observability
- Correct configuration

Kubernetes helps with operations, but it does not fix broken application design.

### 8. Skipping basic `kubectl` inspection commands

Beginners often run `kubectl apply` and then do not inspect what happened.

You should get comfortable with:

```bash
kubectl get pods
kubectl describe pod <pod-name>
kubectl logs <pod-name>
kubectl get services
kubectl get deployments
```

## Related Concepts

- Containers
- Docker images
- Container registries
- Docker Compose
- Pods
- Nodes
- Clusters
- Deployments
- ReplicaSets
- Services
- Labels and selectors
- Rolling updates
- Self-healing systems
- Declarative configuration
- Desired state reconciliation
- Service discovery
- Load balancing
- Health checks
- CI/CD deployment pipelines

## Interview-Level Explanation

Kubernetes is a container orchestration platform. It lets teams describe the desired state of applications, such as how many replicas should run and which container image to use. Kubernetes then schedules Pods onto nodes and continuously reconciles actual state with desired state.

A Pod is the smallest deployable unit and usually wraps one container. A Deployment manages rollout and scaling behavior. The Deployment creates ReplicaSets, and ReplicaSets maintain the desired number of Pods. A Service provides a stable network endpoint for a changing set of Pods selected by labels.

Teams use Kubernetes to standardize deployments, improve reliability, automate restarts and rollouts, and run containerized applications across clusters of machines.

## Hands-On Exercise

Run a simple Deployment and expose it with a Service using `minikube` or `kind`.

This exercise uses `minikube` because it is beginner-friendly for local Service access.

### Step 1: Start minikube

```bash
minikube start
```

Verify your cluster is running:

```bash
kubectl cluster-info
```

Check nodes:

```bash
kubectl get nodes
```

You should see one local node.

### Step 2: Create a Deployment

Create a Deployment using the command line:

```bash
kubectl create deployment hello-kubernetes --image=nginx:1.27
```

Check the Deployment:

```bash
kubectl get deployments
```

Check the Pods:

```bash
kubectl get pods
```

You should see one Pod for the Deployment.

### Step 3: Scale the Deployment

Scale it to 3 replicas:

```bash
kubectl scale deployment hello-kubernetes --replicas=3
```

Check Pods again:

```bash
kubectl get pods
```

You should now see 3 Pods.

This demonstrates that the Deployment wants 3 replicas, and Kubernetes creates the needed Pods.

### Step 4: Inspect the ReplicaSet

Run:

```bash
kubectl get replicasets
```

You should see a ReplicaSet created by the Deployment.

The relationship is:

```text
Deployment: hello-kubernetes
└── ReplicaSet
    ├── Pod
    ├── Pod
    └── Pod
```

### Step 5: Expose the Deployment with a Service

Expose the Deployment:

```bash
kubectl expose deployment hello-kubernetes --type=NodePort --port=80
```

Check Services:

```bash
kubectl get services
```

You should see:

```text
hello-kubernetes   NodePort   ...
```

### Step 6: Access the Service

With minikube, run:

```bash
minikube service hello-kubernetes
```

Or get the URL:

```bash
minikube service hello-kubernetes --url
```

Then test it:

```bash
curl <URL_FROM_MINIKUBE>
```

You should receive the default NGINX HTML response.

### Step 7: Delete one Pod and observe self-healing

List Pods:

```bash
kubectl get pods
```

Delete one Pod:

```bash
kubectl delete pod <pod-name>
```

Immediately check Pods again:

```bash
kubectl get pods
```

You should see Kubernetes creating a replacement Pod.

This is one of the core Kubernetes ideas:

> You declare the desired state. Kubernetes continuously works to maintain it.

### Step 8: View logs

Pick one Pod name:

```bash
kubectl get pods
```

Then run:

```bash
kubectl logs <pod-name>
```

For NGINX, you may see access logs after making requests.

### Step 9: Describe resources

Describe the Deployment:

```bash
kubectl describe deployment hello-kubernetes
```

Describe the Service:

```bash
kubectl describe service hello-kubernetes
```

Describe a Pod:

```bash
kubectl describe pod <pod-name>
```

These commands are important for debugging real Kubernetes issues.

### Step 10: Clean up

Delete the Service:

```bash
kubectl delete service hello-kubernetes
```

Delete the Deployment:

```bash
kubectl delete deployment hello-kubernetes
```

Confirm cleanup:

```bash
kubectl get deployments
kubectl get pods
kubectl get services
```

## Expected Outcome

After completing this exercise, you should be able to explain and demonstrate:

- What Kubernetes does at a basic level
- What a cluster is
- What a node is
- What a Pod is
- Why Deployments are used instead of standalone Pods
- How ReplicaSets maintain the desired number of Pods
- Why Services are needed for stable networking
- How to create a Deployment
- How to scale a Deployment
- How to expose a Deployment with a Service
- How Kubernetes replaces a deleted Pod to maintain desired state

You should be able to summarize the core flow like this:

```text
I create a Deployment.
The Deployment creates a ReplicaSet.
The ReplicaSet creates Pods.
The Pods run containers.
A Service provides stable access to those Pods.
```

## Quiz Questions

1. What is the difference between a Pod, a Deployment, and a Service?

2. Why should you usually avoid relying directly on a Pod IP address?

3. If you scale a Deployment to 3 replicas and then delete one Pod, what should Kubernetes do next and why?

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

Next, learn Kubernetes workload configuration in more detail, especially how applications receive configuration and secrets in a cluster.

A logical next topic is:

- Kubernetes YAML basics
- Labels and selectors
- ConfigMaps
- Secrets
- Environment variables in Pods
- Health checks with readiness and liveness probes
