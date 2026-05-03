# Day 004 — gRPC Fundamentals

Date: 2026-05-03

## Phase

Phase 1 — Backend Foundations

## Learning Objective

By the end of this lesson, you should understand how gRPC enables RPC-style service communication between systems, how Protocol Buffers define APIs and messages, and how clients and servers communicate using unary and streaming calls.

You should be able to explain:

- What gRPC is
- What a `.proto` file is
- What service definitions are
- What clients and servers do in gRPC
- What unary calls are
- What streaming means in gRPC
- Why gRPC is useful in backend and platform systems

## Why This Topic Matters

Many backend systems are made of multiple services.

For example:

```text
Frontend API
   |
   v
User Service
   |
   v
Billing Service
   |
   v
Notification Service
```

These services need to communicate with each other.

A common option is REST over HTTP with JSON. Another option is gRPC.

gRPC is often used in production systems when teams need:

- Strongly typed service contracts
- Fast service-to-service communication
- Efficient binary serialization
- Generated client/server code
- Support for streaming
- Clear API definitions shared across teams
- Better internal APIs between microservices

In platform engineering and distributed systems, gRPC appears often in:

- Kubernetes internals
- Service meshes
- Internal microservice APIs
- Control planes
- Data planes
- Observability agents
- Cloud infrastructure systems
- High-performance backend services

If REST is common for public APIs, gRPC is very common for internal service-to-service communication.

## Simple Explanation

gRPC lets one program call a function on another program as if it were a local function.

Instead of manually building HTTP routes like:

```http
GET /users/123
POST /users
```

You define a service like this:

```proto
service UserService {
  rpc GetUser(GetUserRequest) returns (GetUserResponse);
  rpc CreateUser(CreateUserRequest) returns (CreateUserResponse);
}
```

This says:

- There is a service called `UserService`
- It has a method called `GetUser`
- It has a method called `CreateUser`
- Each method has specific request and response message types

The service definition is written in a `.proto` file.

That `.proto` file becomes the contract between the client and the server.

The gRPC tooling can generate code from the `.proto` file, so both sides agree on:

- Method names
- Request fields
- Response fields
- Data types
- Streaming behavior

In simple terms:

```text
.proto file = shared contract
server = implements the contract
client = calls the contract
gRPC = communication system that connects them
Protocol Buffers = compact message format used to encode data
```

## Real-World Analogy

Imagine a restaurant.

The menu is the contract.

```text
Menu:
- GetUser
- CreateUser
```

The customer cannot order something random that is not on the menu. The kitchen knows exactly what each menu item means.

In gRPC:

- The `.proto` file is the menu
- The client is the customer
- The server is the kitchen
- The request is the order
- The response is the prepared food

For example:

```text
Client says:
"Call GetUser with user_id = 123"

Server responds:
"Here is user 123: name = Alice, email = alice@example.com"
```

The client and server both understand the same contract because they both use the same `.proto` definition.

## Technical Explanation

gRPC is a high-performance RPC framework.

RPC means Remote Procedure Call.

A procedure is a function or method. A remote procedure call means calling a function that runs on another machine or process.

Instead of thinking only in terms of HTTP resources, such as:

```http
GET /users/123
```

With gRPC, you think in terms of service methods:

```text
UserService.GetUser(...)
```

A gRPC system usually has these parts:

```text
.proto file
   |
   v
code generation
   |
   +--> generated client code
   |
   +--> generated server interface/code
              |
              v
        server implements service methods
              ^
              |
        client calls service methods
```

### Protocol Buffers

Protocol Buffers, often called protobuf, are used to define the structure of messages.

A protobuf message looks like this:

```proto
message User {
  string id = 1;
  string name = 2;
  string email = 3;
}
```

Each field has:

- A type: `string`
- A name: `id`
- A field number: `1`

The field number is important because protobuf encodes messages in a compact binary format. The field number is used during serialization.

Example:

```proto
string id = 1;
```

Means:

```text
Field type: string
Field name: id
Field number: 1
```

Do not casually change field numbers once messages are used in production. Existing clients and servers may depend on them.

### Service Definitions

A service definition describes the RPC methods available on a server.

Example:

```proto
service UserService {
  rpc GetUser(GetUserRequest) returns (GetUserResponse);
}
```

This defines one RPC method:

```text
Method: GetUser
Input: GetUserRequest
Output: GetUserResponse
```

The server must implement `GetUser`.

The client can call `GetUser`.

### Clients and Servers

In gRPC:

- The server exposes service methods.
- The client calls those service methods.
- The `.proto` file defines the contract.
- Generated code helps both sides use the same API safely.

A typical flow:

```text
1. Write user.proto
2. Generate client/server code
3. Server implements UserService
4. Client creates a gRPC connection
5. Client calls GetUser
6. Server receives request
7. Server sends response
```

### Unary Calls

A unary call is the simplest type of gRPC call.

It means:

```text
one request -> one response
```

Example:

```proto
rpc GetUser(GetUserRequest) returns (GetUserResponse);
```

The client sends one `GetUserRequest`.

The server sends one `GetUserResponse`.

This is similar to a normal HTTP request/response.

### Streaming Calls

gRPC also supports streaming.

There are four main call types:

#### 1. Unary

```text
one request -> one response
```

Example:

```proto
rpc GetUser(GetUserRequest) returns (GetUserResponse);
```

#### 2. Server streaming

```text
one request -> many responses
```

Example:

```proto
rpc ListUsers(ListUsersRequest) returns (stream User);
```

The client sends one request. The server streams multiple users back.

#### 3. Client streaming

```text
many requests -> one response
```

Example:

```proto
rpc UploadUsers(stream CreateUserRequest) returns (UploadUsersResponse);
```

The client sends many user creation requests. The server returns one final response.

#### 4. Bidirectional streaming

```text
many requests -> many responses
```

Example:

```proto
rpc Chat(stream ChatMessage) returns (stream ChatMessage);
```

Both sides can send messages over time.

This is useful for real-time systems, agents, telemetry, logs, chat, and long-lived service communication.

### gRPC and HTTP/2

gRPC commonly uses HTTP/2 as its transport layer.

HTTP/2 gives gRPC features like:

- Multiplexing multiple streams over one connection
- Efficient binary framing
- Header compression
- Long-lived connections
- Streaming support

This is one reason gRPC is useful for internal service communication.

## Practical Example

Here is a small `user.proto` file for a `UserService`.

```proto
syntax = "proto3";

package users.v1;

option go_package = "example.com/myapp/users/v1;usersv1";

service UserService {
  rpc GetUser(GetUserRequest) returns (GetUserResponse);
  rpc CreateUser(CreateUserRequest) returns (CreateUserResponse);
}

message User {
  string id = 1;
  string name = 2;
  string email = 3;
}

message GetUserRequest {
  string id = 1;
}

message GetUserResponse {
  User user = 1;
}

message CreateUserRequest {
  string name = 1;
  string email = 2;
}

message CreateUserResponse {
  User user = 1;
}
```

This file defines:

```text
Package:
- users.v1

Service:
- UserService

Methods:
- GetUser
- CreateUser

Messages:
- User
- GetUserRequest
- GetUserResponse
- CreateUserRequest
- CreateUserResponse
```

The important part is the service contract:

```proto
service UserService {
  rpc GetUser(GetUserRequest) returns (GetUserResponse);
  rpc CreateUser(CreateUserRequest) returns (CreateUserResponse);
}
```

That means a client can call:

```text
UserService.GetUser
UserService.CreateUser
```

The server must implement those methods.

### Architecture View

```text
                    shared user.proto
                           |
          -------------------------------------
          |                                   |
          v                                   v
  generated client code              generated server code
          |                                   |
          v                                   v
  UserService client  ---- gRPC ---->  UserService server
          |                                   |
          v                                   v
  calls GetUser/CreateUser          implements GetUser/CreateUser
```

### Example Request/Response Thinking

For `GetUser`:

```text
Request:
{
  id: "user-123"
}

Response:
{
  user: {
    id: "user-123",
    name: "Alice",
    email: "alice@example.com"
  }
}
```

For `CreateUser`:

```text
Request:
{
  name: "Bob",
  email: "bob@example.com"
}

Response:
{
  user: {
    id: "generated-user-id",
    name: "Bob",
    email: "bob@example.com"
  }
}
```

In actual gRPC, these are serialized as protobuf binary messages, not JSON by default.

## Official Documentation To Read

- [gRPC — Introduction](https://grpc.io/docs/what-is-grpc/introduction/)
- [gRPC — Core concepts, architecture and lifecycle](https://grpc.io/docs/what-is-grpc/core-concepts/)

## Good Reads

- [gRPC Documentation](https://grpc.io/docs/)

## Where This Appears in Production

gRPC appears in production anywhere services need fast, structured communication.

Common examples:

### Internal Microservices

A public API service may receive HTTP/JSON requests from users, then call internal services using gRPC.

```text
Browser
  |
  v
Public REST API
  |
  v
UserService via gRPC
  |
  v
Database
```

### Platform Control Planes

Platform systems often have control planes that coordinate work across many components.

Example:

```text
Control Plane
  |
  v
Worker Agent via gRPC
```

The control plane can send instructions to agents, and agents can report status back.

### Kubernetes and Infrastructure Systems

Many infrastructure systems use RPC-style APIs internally because they need clear contracts and efficient communication.

### Observability Pipelines

Telemetry systems may use gRPC to send traces, metrics, and logs from agents to collectors.

```text
Application
  |
  v
Telemetry Agent
  |
  v
Collector via gRPC
  |
  v
Storage Backend
```

### Mobile and Backend Communication

Some companies use gRPC or gRPC-related technologies for communication between mobile clients and backend systems, especially when strong contracts and performance are important.

### Service Meshes

Service meshes and proxies often need to understand, route, observe, and secure service-to-service traffic. gRPC traffic is common in these environments.

## Common Beginner Mistakes

### 1. Thinking gRPC is just REST with different syntax

gRPC is not just REST with a different file format.

REST usually models resources:

```text
GET /users/123
POST /users
```

gRPC models service methods:

```text
UserService.GetUser
UserService.CreateUser
```

Both are useful, but they encourage different API design styles.

### 2. Ignoring the `.proto` file as the contract

The `.proto` file is not just a helper file.

It is the API contract.

Changing it carelessly can break clients and servers.

### 3. Reusing field numbers incorrectly

In protobuf, field numbers matter.

This is dangerous:

```proto
message User {
  string id = 1;
  string name = 2;
}
```

Then later changing it to:

```proto
message User {
  string name = 1;
  string id = 2;
}
```

That can break compatibility because field numbers changed meaning.

### 4. Designing gRPC APIs like database tables

A protobuf message is not automatically the same thing as your database schema.

Avoid exposing internal database structure directly as your external service contract.

### 5. Forgetting about deadlines and timeouts

Production gRPC calls should usually have deadlines or timeouts.

Without them, clients may wait too long for broken services.

### 6. Forgetting about backwards compatibility

In real systems, old clients and new servers often exist at the same time.

You need to evolve proto files carefully.

### 7. Assuming streaming is always needed

Streaming is powerful, but it adds complexity.

If your operation is simply:

```text
one request -> one response
```

Use a unary call.

### 8. Confusing protobuf with gRPC

They are related, but not the same.

```text
gRPC = RPC framework
Protocol Buffers = data definition and serialization format
```

gRPC commonly uses protobuf, but they are separate concepts.

## Related Concepts

- REST APIs
- HTTP/2
- Protocol Buffers
- Serialization
- API contracts
- RPC
- Service discovery
- Load balancing
- Deadlines and timeouts
- Retries
- Idempotency
- Backward compatibility
- Schema evolution
- Streaming
- Microservices
- Service mesh
- Observability
- Distributed tracing

## Interview-Level Explanation

gRPC is a high-performance RPC framework commonly used for service-to-service communication. APIs are defined in `.proto` files using Protocol Buffers. The proto file defines services, RPC methods, and request/response message types. From this contract, code can be generated for clients and servers. gRPC supports unary calls, where one request returns one response, and streaming calls, including server streaming, client streaming, and bidirectional streaming. It commonly uses HTTP/2, which enables efficient multiplexed connections and streaming.

## Hands-On Exercise

Create a small proto file for a `UserService` with `GetUser` and `CreateUser` methods.

### Step 1: Create a project folder

```bash
mkdir grpc-user-service
cd grpc-user-service
```

### Step 2: Create a proto folder

```bash
mkdir -p proto/users/v1
```

### Step 3: Create the proto file

Create this file:

```text
proto/users/v1/user.proto
```

Add the following content:

```proto
syntax = "proto3";

package users.v1;

service UserService {
  rpc GetUser(GetUserRequest) returns (GetUserResponse);
  rpc CreateUser(CreateUserRequest) returns (CreateUserResponse);
}

message User {
  string id = 1;
  string name = 2;
  string email = 3;
}

message GetUserRequest {
  string id = 1;
}

message GetUserResponse {
  User user = 1;
}

message CreateUserRequest {
  string name = 1;
  string email = 2;
}

message CreateUserResponse {
  User user = 1;
}
```

### Step 4: Read the service definition out loud

Focus on this part:

```proto
service UserService {
  rpc GetUser(GetUserRequest) returns (GetUserResponse);
  rpc CreateUser(CreateUserRequest) returns (CreateUserResponse);
}
```

Explain it in plain English:

```text
UserService exposes two methods.

GetUser takes a GetUserRequest and returns a GetUserResponse.

CreateUser takes a CreateUserRequest and returns a CreateUserResponse.
```

### Step 5: Identify the unary calls

Both methods are unary calls:

```proto
rpc GetUser(GetUserRequest) returns (GetUserResponse);
rpc CreateUser(CreateUserRequest) returns (CreateUserResponse);
```

Because each method has:

```text
one request -> one response
```

### Step 6: Add comments to the proto file

Update the file with comments:

```proto
syntax = "proto3";

package users.v1;

// UserService defines RPC methods for working with users.
service UserService {
  // GetUser fetches a single user by ID.
  rpc GetUser(GetUserRequest) returns (GetUserResponse);

  // CreateUser creates a new user.
  rpc CreateUser(CreateUserRequest) returns (CreateUserResponse);
}

// User represents a user returned by the service.
message User {
  string id = 1;
  string name = 2;
  string email = 3;
}

// Request message for GetUser.
message GetUserRequest {
  string id = 1;
}

// Response message for GetUser.
message GetUserResponse {
  User user = 1;
}

// Request message for CreateUser.
message CreateUserRequest {
  string name = 1;
  string email = 2;
}

// Response message for CreateUser.
message CreateUserResponse {
  User user = 1;
}
```

### Step 7: Add one streaming example as a comment

Do not implement it yet. Just add this comment near the service so you understand the syntax:

```proto
// Example future streaming method:
// rpc ListUsers(ListUsersRequest) returns (stream User);
```

That means:

```text
one request -> many User responses
```

### Step 8: Write a short explanation in your own words

Create a file:

```bash
touch NOTES.md
```

In `NOTES.md`, answer:

```markdown
# gRPC Notes

## What is the proto file?

## What is UserService?

## What are GetUser and CreateUser?

## Are these unary or streaming calls?

## What does the server do?

## What does the client do?
```

Keep the answers short. The goal is clarity, not length.

## Expected Outcome

After the exercise, you should be able to explain:

- A `.proto` file defines a service contract.
- `UserService` is the service exposed by the server.
- `GetUser` and `CreateUser` are RPC methods.
- `GetUserRequest` and `CreateUserRequest` are input message types.
- `GetUserResponse` and `CreateUserResponse` are output message types.
- A gRPC client calls methods defined in the proto file.
- A gRPC server implements methods defined in the proto file.
- A unary call means one request and one response.
- Streaming means one side or both sides can send multiple messages over time.
- Protocol Buffers define structured messages and serialize them efficiently.

You should also be comfortable reading this and explaining it:

```proto
rpc GetUser(GetUserRequest) returns (GetUserResponse);
```

As:

```text
The client calls GetUser with a GetUserRequest.
The server responds with a GetUserResponse.
```

## Quiz Questions

1. What is the role of a `.proto` file in a gRPC system?

2. What is the difference between a unary gRPC call and a server-streaming gRPC call?

3. In this method definition, what is the request type and what is the response type?

```proto
rpc CreateUser(CreateUserRequest) returns (CreateUserResponse);
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

Next, learn how to implement a small gRPC server and client in one programming language.

A good next topic is:

```text
Building a Basic gRPC Client and Server
```

That will connect today’s proto contract to real running code.
