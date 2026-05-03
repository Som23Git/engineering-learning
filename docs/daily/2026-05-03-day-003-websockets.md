# Day 003 — WebSockets

Date: 2026-05-03

## Phase

Phase 1 — Backend Foundations

## Learning Objective

By the end of this lesson, you should understand when persistent bidirectional connections are useful and how WebSockets differ from normal HTTP request-response communication.

You should be able to explain:

- What a WebSocket is
- Why WebSockets are used for realtime communication
- When WebSockets are a good fit
- When normal HTTP is still the better choice
- How a browser client connects to a WebSocket server

## Why This Topic Matters

Most backend systems start with HTTP APIs.

A client sends a request:

```text
Client -> Server: GET /orders/123
Server -> Client: 200 OK with order data
```

That works well for many systems.

But some products need the server to send updates immediately without waiting for the client to ask again.

Examples:

- Chat messages
- Live dashboards
- Multiplayer games
- Collaborative editing
- Trading/market data
- Notifications
- Realtime logs
- Device telemetry

With plain HTTP, the client usually has to keep asking:

```text
"Any new messages?"
"Any new messages?"
"Any new messages?"
```

This is called polling. It can be wasteful and slow.

WebSockets allow one long-lived connection where both sides can send messages at any time:

```text
Client <---- persistent connection ----> Server
```

This matters in backend and platform engineering because persistent connections change how you think about:

- Load balancing
- Scaling
- Timeouts
- Connection limits
- Deployments
- Observability
- Reliability
- Backpressure
- Authentication and authorization

WebSockets are simple to use at a small scale, but they become important infrastructure design decisions in production.

## Simple Explanation

HTTP is like asking a question and getting one answer.

```text
Client: What is my account balance?
Server: Your balance is $100.
```

After the answer, that interaction is done.

A WebSocket is different. The client and server open a connection and keep it open.

```text
Client: Let's keep this connection open.
Server: Okay.
Client: Message 1
Server: Message 2
Server: Message 3
Client: Message 4
```

Either side can send messages whenever it needs to.

Use WebSockets when the server needs to push updates to the client quickly.

Do not use WebSockets just because they sound modern. If the client only needs to fetch data occasionally, normal HTTP is simpler and usually better.

## Real-World Analogy

Think of HTTP like ordering at a restaurant counter.

You walk up, ask for something, get your response, then leave the counter.

```text
You: Can I have a coffee?
Cashier: Yes, here is your coffee.
```

If you want something else, you go back and ask again.

WebSockets are more like being on a phone call.

Once the call is connected, both people can talk whenever they need to.

```text
You: I am ready.
Other person: New update just arrived.
You: Got it.
Other person: Another update arrived.
```

The phone call stays open until someone hangs up.

That is the key idea: WebSockets keep a communication channel open.

## Technical Explanation

WebSockets start with an HTTP request, but then the connection is upgraded to the WebSocket protocol.

At a high level:

```text
1. Browser sends an HTTP request asking to upgrade the connection.
2. Server accepts the upgrade.
3. The connection becomes a WebSocket connection.
4. Client and server exchange WebSocket messages over the same TCP connection.
5. Either side can close the connection.
```

Normal HTTP request-response:

```text
Client                  Server
  |                       |
  | ---- HTTP Request --> |
  | <-- HTTP Response --- |
  |                       |
Connection may close or return to pool.
```

WebSocket communication:

```text
Client                  Server
  |                       |
  | -- HTTP Upgrade ----> |
  | <-- Upgrade OK ------ |
  |                       |
  | <== WebSocket open ==>|
  |                       |
  | ---- message -------> |
  | <---- message ------- |
  | <---- message ------- |
  | ---- message -------> |
  |                       |
```

Important properties:

| Concept | HTTP Request-Response | WebSocket |
|---|---|---|
| Connection style | Short interaction | Long-lived connection |
| Direction | Client initiates each request | Both client and server can send |
| Best for | CRUD APIs, fetching resources | Realtime updates |
| Server push | Not natural | Built in |
| Scaling complexity | Usually simpler | More complex |
| Common payload | JSON over HTTP | Text/binary messages, often JSON |
| Browser API | `fetch`, forms, navigation | `WebSocket` API |

WebSocket URLs usually use:

```text
ws://example.com
wss://example.com
```

`ws://` is unencrypted WebSocket.

`wss://` is WebSocket over TLS, similar to how `https://` is encrypted HTTP.

In production, prefer `wss://`.

## Practical Example

Here is a tiny WebSocket echo server.

An echo server sends back whatever message it receives.

Architecture:

```text
Browser Client
     |
     | WebSocket connection: ws://localhost:8080
     |
WebSocket Echo Server
```

When the browser sends:

```text
hello
```

The server replies:

```text
echo: hello
```

### Server: `server.mjs`

This example uses Node.js with the `ws` package.

```js
import { WebSocketServer } from "ws";

const wss = new WebSocketServer({ port: 8080 });

wss.on("connection", (socket, request) => {
  console.log("Client connected from:", request.socket.remoteAddress);

  socket.send("Connected to WebSocket echo server");

  socket.on("message", (data) => {
    const message = data.toString();
    console.log("Received:", message);

    socket.send(`echo: ${message}`);
  });

  socket.on("close", () => {
    console.log("Client disconnected");
  });

  socket.on("error", (error) => {
    console.error("WebSocket error:", error);
  });
});

console.log("WebSocket server running on ws://localhost:8080");
```

### Browser Client: `index.html`

```html
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>WebSocket Echo Client</title>
  </head>
  <body>
    <h1>WebSocket Echo Client</h1>

    <p>Status: <span id="status">Not connected</span></p>

    <input id="messageInput" placeholder="Type a message" />
    <button id="sendButton">Send</button>

    <h2>Messages</h2>
    <pre id="messages"></pre>

    <script>
      const statusEl = document.getElementById("status");
      const messagesEl = document.getElementById("messages");
      const inputEl = document.getElementById("messageInput");
      const sendButton = document.getElementById("sendButton");

      const socket = new WebSocket("ws://localhost:8080");

      function log(message) {
        messagesEl.textContent += message + "\n";
      }

      socket.addEventListener("open", () => {
        statusEl.textContent = "Connected";
        log("Connected to server");
      });

      socket.addEventListener("message", (event) => {
        log("Server: " + event.data);
      });

      socket.addEventListener("close", () => {
        statusEl.textContent = "Disconnected";
        log("Connection closed");
      });

      socket.addEventListener("error", () => {
        statusEl.textContent = "Error";
        log("WebSocket error occurred");
      });

      sendButton.addEventListener("click", () => {
        const message = inputEl.value;

        if (!message) {
          return;
        }

        log("Client: " + message);
        socket.send(message);
        inputEl.value = "";
      });
    </script>
  </body>
</html>
```

The important browser line is:

```js
const socket = new WebSocket("ws://localhost:8080");
```

That creates the persistent connection.

Sending data:

```js
socket.send("hello");
```

Receiving data:

```js
socket.addEventListener("message", (event) => {
  console.log(event.data);
});
```

## Official Documentation To Read

- [MDN — The WebSocket API](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API)

## Good Reads

- [MDN — Writing WebSocket client applications](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API/Writing_WebSocket_client_applications)

## Where This Appears in Production

WebSockets appear in systems where waiting for the next HTTP request is too slow or inefficient.

Common production uses:

- Chat applications
- Customer support messaging
- Collaborative documents
- Live sports scores
- Stock price updates
- Multiplayer games
- Browser-based terminals
- Live infrastructure dashboards
- CI/CD build logs
- Incident management dashboards
- IoT device control panels
- Realtime notifications

Production concerns include:

### 1. Load Balancers

WebSockets are long-lived connections. Your load balancer must support connection upgrades and long idle timeouts.

If the load balancer closes idle connections too aggressively, clients may disconnect unexpectedly.

### 2. Horizontal Scaling

With normal HTTP, any request can often go to any server.

With WebSockets, a client stays connected to one server.

```text
Client A -> Server 1
Client B -> Server 2
Client C -> Server 1
```

If Client A sends a chat message and Client B is connected to another server, Server 1 may need to publish that message through shared infrastructure.

Common patterns:

```text
Server 1 -> Pub/Sub or Message Broker -> Server 2
```

### 3. Authentication

You still need to know who the user is.

A common flow is:

```text
1. User logs in over HTTP.
2. Browser gets a session cookie or token.
3. Browser opens WebSocket connection.
4. Server validates the user during connection setup.
```

Do not assume a WebSocket is safe just because it is already connected.

### 4. Observability

You need to monitor:

- Number of active connections
- Connection duration
- Message rate
- Message size
- Errors
- Disconnects
- Reconnect storms
- Server memory usage

### 5. Deployments

When deploying a new server version, existing WebSocket clients may still be connected.

You need graceful shutdown behavior:

```text
1. Stop accepting new connections.
2. Let existing connections finish or notify them.
3. Close old connections safely.
4. Start new version.
```

## Common Beginner Mistakes

1. **Using WebSockets when HTTP is enough**

   If the client only needs to fetch data on page load, use HTTP.

2. **Confusing WebSockets with REST**

   REST is usually about resources and request-response APIs.

   WebSockets are message-based persistent connections.

3. **Forgetting that connections can drop**

   WebSocket connections are not permanent forever.

   Networks fail. Browsers sleep. Mobile devices switch networks. Servers restart.

   Clients usually need reconnect logic.

4. **Not thinking about authentication**

   A WebSocket connection still needs access control.

   You must know who connected and what they are allowed to do.

5. **Sending huge messages**

   WebSockets are not a reason to send massive payloads casually.

   Large messages can create memory pressure and slow clients.

6. **Ignoring backpressure**

   If the server sends messages faster than the client can process them, memory can build up.

7. **Assuming every server instance knows every client**

   In a scaled system, clients are spread across many server instances.

   You may need shared state, pub/sub, or a message broker.

8. **Not using `wss://` in production**

   Use encrypted WebSocket connections in production, just like HTTPS.

9. **Treating WebSockets like a database**

   WebSockets are a communication channel, not durable storage.

   If messages must not be lost, you need persistence or a message queue.

## Related Concepts

- HTTP request-response
- HTTP upgrade mechanism
- TCP connections
- TLS
- `ws://` and `wss://`
- Polling
- Long polling
- Server-Sent Events
- Pub/Sub
- Message brokers
- Load balancing
- Sticky sessions
- Connection timeouts
- Heartbeats and ping/pong
- Reconnection logic
- Backpressure
- Realtime systems
- Event-driven architecture

## Interview-Level Explanation

WebSockets provide a persistent bidirectional connection between a client and server. Unlike normal HTTP, where the client sends a request and receives a response, WebSockets allow either side to send messages at any time after the connection is established.

They are useful for realtime features such as chat, notifications, live dashboards, collaborative editing, and games. They are not a replacement for REST APIs. For normal CRUD operations, HTTP is usually simpler. In production, WebSockets require careful handling of authentication, load balancing, connection limits, reconnects, graceful shutdown, and horizontal scaling.

## Hands-On Exercise

Build and run a tiny WebSocket echo server and connect to it from a browser client.

### Step 1: Create a project directory

```bash
mkdir websocket-echo-demo
cd websocket-echo-demo
```

### Step 2: Initialize a Node.js project

```bash
npm init -y
```

### Step 3: Install the WebSocket package

```bash
npm install ws
```

### Step 4: Create the server file

Create a file named:

```text
server.mjs
```

Add this code:

```js
import { WebSocketServer } from "ws";

const wss = new WebSocketServer({ port: 8080 });

wss.on("connection", (socket, request) => {
  console.log("Client connected from:", request.socket.remoteAddress);

  socket.send("Connected to WebSocket echo server");

  socket.on("message", (data) => {
    const message = data.toString();
    console.log("Received:", message);

    socket.send(`echo: ${message}`);
  });

  socket.on("close", () => {
    console.log("Client disconnected");
  });

  socket.on("error", (error) => {
    console.error("WebSocket error:", error);
  });
});

console.log("WebSocket server running on ws://localhost:8080");
```

### Step 5: Run the server

```bash
node server.mjs
```

You should see:

```text
WebSocket server running on ws://localhost:8080
```

### Step 6: Create the browser client

Create a file named:

```text
index.html
```

Add this code:

```html
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>WebSocket Echo Client</title>
  </head>
  <body>
    <h1>WebSocket Echo Client</h1>

    <p>Status: <span id="status">Not connected</span></p>

    <input id="messageInput" placeholder="Type a message" />
    <button id="sendButton">Send</button>

    <h2>Messages</h2>
    <pre id="messages"></pre>

    <script>
      const statusEl = document.getElementById("status");
      const messagesEl = document.getElementById("messages");
      const inputEl = document.getElementById("messageInput");
      const sendButton = document.getElementById("sendButton");

      const socket = new WebSocket("ws://localhost:8080");

      function log(message) {
        messagesEl.textContent += message + "\n";
      }

      socket.addEventListener("open", () => {
        statusEl.textContent = "Connected";
        log("Connected to server");
      });

      socket.addEventListener("message", (event) => {
        log("Server: " + event.data);
      });

      socket.addEventListener("close", () => {
        statusEl.textContent = "Disconnected";
        log("Connection closed");
      });

      socket.addEventListener("error", () => {
        statusEl.textContent = "Error";
        log("WebSocket error occurred");
      });

      sendButton.addEventListener("click", () => {
        const message = inputEl.value;

        if (!message) {
          return;
        }

        log("Client: " + message);
        socket.send(message);
        inputEl.value = "";
      });
    </script>
  </body>
</html>
```

### Step 7: Open the browser client

Open `index.html` in your browser.

You should see the status change to:

```text
Connected
```

Type a message and click **Send**.

Example:

```text
Client: hello
Server: echo: hello
```

### Step 8: Observe the server logs

In your terminal, you should see logs like:

```text
Client connected from: ::1
Received: hello
```

### Step 9: Test disconnect behavior

Stop the server with:

```bash
Ctrl+C
```

The browser should eventually show that the connection closed or errored.

This is important: WebSocket connections can disappear. Production clients need reconnect logic.

### Step 10: Restart the server

Run again:

```bash
node server.mjs
```

Refresh the browser page and reconnect.

## Expected Outcome

After this exercise, you should be able to explain the difference between HTTP request-response and persistent WebSocket communication.

You should be able to say:

- HTTP request-response is client-initiated and usually short-lived.
- A WebSocket connection stays open.
- After a WebSocket is connected, both client and server can send messages.
- WebSockets are useful when the server needs to push realtime updates.
- WebSockets add production concerns around connection management, scaling, authentication, and reliability.

You should also have a working local example where:

```text
Browser sends message -> Server receives message -> Server echoes message back
```

## Quiz Questions

1. What is the main difference between normal HTTP request-response communication and WebSocket communication?

2. Name two production features where WebSockets are a good fit.

3. Why can WebSockets be harder to scale horizontally than normal stateless HTTP APIs?

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

Next, learn how backend services handle **authentication and sessions**, especially how a user’s identity is carried from normal HTTP requests into longer-lived communication patterns like WebSockets.
