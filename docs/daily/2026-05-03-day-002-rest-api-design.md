# Day 002 — REST API Design

Date: 2026-05-03

## Phase

Phase 1 — Backend Foundations

## Learning Objective

By the end of this lesson, you should understand how REST-style APIs expose application functionality through resources, HTTP methods, status codes, request validation, and idempotency.

You should be able to design basic REST endpoints for a todo application, including:

- Create a todo
- List todos
- Update a todo
- Delete a todo

## Why This Topic Matters

REST API design is one of the most common backend engineering skills.

In real systems, APIs are how different parts of software communicate:

- Frontend apps call backend APIs.
- Mobile apps call backend APIs.
- Internal services call each other through APIs.
- Platform tools expose APIs for automation.
- Cloud services expose APIs to manage infrastructure.

A poorly designed API can cause confusion, bugs, security issues, and operational problems. A well-designed API is predictable, easy to test, easier to monitor, and easier to evolve over time.

As a backend or platform engineer, you need to design APIs that other engineers can use safely and consistently.

## Simple Explanation

A REST API is a way for clients to work with things in your application using HTTP.

Those “things” are called **resources**.

For a todo app, the main resource is:

```text
todo
```

Usually, REST APIs use nouns in URLs:

```text
/todos
/todos/{todoId}
```

Then they use HTTP methods to describe the action:

| Action | HTTP Method | Example |
|---|---:|---|
| Create a todo | `POST` | `POST /todos` |
| List todos | `GET` | `GET /todos` |
| Get one todo | `GET` | `GET /todos/123` |
| Update a todo | `PUT` or `PATCH` | `PATCH /todos/123` |
| Delete a todo | `DELETE` | `DELETE /todos/123` |

The URL says **what resource** you are working with.

The HTTP method says **what you want to do**.

The status code says **what happened**.

Example:

```http
POST /todos
```

Response:

```http
201 Created
```

That means: “The todo was created successfully.”

## Real-World Analogy

Think about a restaurant ordering system.

The **menu item** is the resource.

The **action** depends on what you are doing:

- Ask for the menu: `GET /menu`
- Place an order: `POST /orders`
- Change an order: `PATCH /orders/123`
- Cancel an order: `DELETE /orders/123`

The waiter does not need you to say:

```text
/createNewOrderNow
/removeThisOrderNow
/showAllOrdersNow
```

Instead, the restaurant has clear objects:

```text
/orders
/orders/123
/menu
```

And clear actions.

REST APIs work the same way: clear resources, clear methods, clear responses.

## Technical Explanation

REST-style API design is based on modeling your application as resources exposed through HTTP.

A **resource** is usually a domain object or collection, such as:

```text
/users
/orders
/payments
/todos
/projects
```

Each resource has a URI.

Examples:

```text
/todos
/todos/42
/users/1001
/users/1001/todos
```

HTTP methods define the operation.

Common methods include:

| Method | Meaning | Usually Has Body? | Safe? | Idempotent? |
|---|---|---:|---:|---:|
| `GET` | Read a resource | No | Yes | Yes |
| `POST` | Create or trigger processing | Yes | No | Usually no |
| `PUT` | Replace a resource | Yes | No | Yes |
| `PATCH` | Partially update a resource | Yes | No | Not always |
| `DELETE` | Delete a resource | Usually no | No | Yes |

Two important terms:

### Safe

A method is **safe** if it does not change server state.

`GET` should be safe.

This means this request should not create, update, or delete data:

```http
GET /todos
```

### Idempotent

A method is **idempotent** if making the same request multiple times has the same final effect as making it once.

Example:

```http
DELETE /todos/123
```

If the todo exists, the first request deletes it.

If you send the same delete request again, the todo is still deleted. The final state is the same.

That makes `DELETE` idempotent.

Another example:

```http
PUT /todos/123
```

With body:

```json
{
  "title": "Buy milk",
  "completed": false
}
```

Sending that same `PUT` request once or five times leaves the todo in the same final state.

But this is usually **not** idempotent:

```http
POST /todos
```

If you send it five times, you may create five todos.

### Status Codes

HTTP status codes communicate the result.

Common REST API status codes:

| Status Code | Meaning | Example Use |
|---:|---|---|
| `200 OK` | Request succeeded | List todos, update response |
| `201 Created` | Resource created | Create todo |
| `204 No Content` | Success with no response body | Delete todo |
| `400 Bad Request` | Invalid request format or invalid input | Missing title |
| `401 Unauthorized` | Authentication required or invalid | Missing token |
| `403 Forbidden` | Authenticated but not allowed | User cannot access todo |
| `404 Not Found` | Resource does not exist | Todo ID not found |
| `409 Conflict` | Request conflicts with current state | Duplicate unique value |
| `422 Unprocessable Content` | Request understood but validation failed | Invalid business rules |
| `500 Internal Server Error` | Server failed unexpectedly | Bug, dependency failure |

### Request Validation

APIs should validate client input before changing data.

For a todo app, a create request might require:

```json
{
  "title": "Buy groceries"
}
```

Validation rules might be:

- `title` is required
- `title` must be a string
- `title` cannot be empty
- `completed` must be a boolean if provided
- Unknown fields may be rejected or ignored depending on API design

Bad request example:

```json
{
  "title": ""
}
```

Possible response:

```http
400 Bad Request
```

```json
{
  "error": "validation_failed",
  "message": "title must not be empty"
}
```

Good REST APIs are predictable not only when things work, but also when things fail.

## Practical Example

Here is a REST-style API design for a todo app.

### Resource Model

A todo resource could look like this:

```json
{
  "id": "todo_123",
  "title": "Read about HTTP methods",
  "completed": false,
  "createdAt": "2026-05-03T10:00:00Z",
  "updatedAt": "2026-05-03T10:00:00Z"
}
```

### Endpoints

```text
POST   /todos          Create a todo
GET    /todos          List todos
GET    /todos/{id}     Get one todo
PATCH  /todos/{id}     Partially update a todo
DELETE /todos/{id}     Delete a todo
```

### Create Todo

Request:

```bash
curl -X POST https://api.example.com/todos \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Learn REST API design"
  }'
```

Response:

```http
201 Created
Content-Type: application/json
```

```json
{
  "id": "todo_123",
  "title": "Learn REST API design",
  "completed": false,
  "createdAt": "2026-05-03T10:00:00Z",
  "updatedAt": "2026-05-03T10:00:00Z"
}
```

### List Todos

Request:

```bash
curl https://api.example.com/todos
```

Response:

```http
200 OK
Content-Type: application/json
```

```json
{
  "items": [
    {
      "id": "todo_123",
      "title": "Learn REST API design",
      "completed": false,
      "createdAt": "2026-05-03T10:00:00Z",
      "updatedAt": "2026-05-03T10:00:00Z"
    }
  ]
}
```

For production APIs, list endpoints often need pagination:

```text
GET /todos?limit=20&cursor=abc123
```

### Update Todo

Use `PATCH` when updating only part of the resource.

Request:

```bash
curl -X PATCH https://api.example.com/todos/todo_123 \
  -H "Content-Type: application/json" \
  -d '{
    "completed": true
  }'
```

Response:

```http
200 OK
Content-Type: application/json
```

```json
{
  "id": "todo_123",
  "title": "Learn REST API design",
  "completed": true,
  "createdAt": "2026-05-03T10:00:00Z",
  "updatedAt": "2026-05-03T10:05:00Z"
}
```

### Delete Todo

Request:

```bash
curl -X DELETE https://api.example.com/todos/todo_123
```

Response:

```http
204 No Content
```

No response body is needed.

### Error Example

Request:

```bash
curl -X POST https://api.example.com/todos \
  -H "Content-Type: application/json" \
  -d '{
    "title": ""
  }'
```

Response:

```http
400 Bad Request
Content-Type: application/json
```

```json
{
  "error": "validation_failed",
  "message": "title must not be empty"
}
```

## Official Documentation To Read

- [MDN — HTTP request methods](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Methods)
- [MDN — HTTP response status codes](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status)

## Good Reads

- [Microsoft REST API Guidelines](https://github.com/microsoft/api-guidelines)

## Where This Appears in Production

REST APIs appear in many production systems:

- Public APIs for customers and partners
- Internal APIs between frontend and backend teams
- Microservice-to-microservice communication
- Cloud provider APIs
- Kubernetes APIs
- CI/CD platform APIs
- Observability platform APIs
- Admin dashboards
- Billing and payment systems
- User management services

In production, REST API design affects:

### Reliability

Clients retry failed requests. If your API is not designed with idempotency in mind, retries can accidentally create duplicate data.

Example problem:

```text
Client sends POST /payments
Network times out
Client retries POST /payments
User is charged twice
```

This is why idempotency matters.

### Observability

APIs are monitored with metrics like:

```text
request_count
request_latency
error_rate
status_code_count
```

Good endpoint design makes dashboards and alerts easier to understand.

For example:

```text
GET /todos
POST /todos
PATCH /todos/{id}
DELETE /todos/{id}
```

is easier to reason about than:

```text
POST /doTodoThing
POST /todoAction
POST /modifyTodo
```

### Security

APIs need authentication, authorization, and input validation.

Example:

```text
User A should not be able to access User B's todo.
```

A request like this must check ownership:

```http
GET /todos/todo_123
```

### Backward Compatibility

Once clients depend on an API, changing it becomes risky.

Removing a field, changing a status code, or changing response shape can break clients.

Production APIs need careful versioning and compatibility planning.

## Common Beginner Mistakes

1. **Using verbs in URLs instead of resources**

   Avoid:

   ```text
   /createTodo
   /deleteTodo
   /updateTodo
   ```

   Prefer:

   ```text
   POST /todos
   DELETE /todos/{id}
   PATCH /todos/{id}
   ```

2. **Using `POST` for everything**

   This makes the API harder to understand, cache, retry, monitor, and secure.

   Avoid:

   ```text
   POST /todos/list
   POST /todos/delete
   POST /todos/update
   ```

3. **Returning `200 OK` for every response**

   Status codes should communicate what happened.

   Better examples:

   ```text
   201 Created
   400 Bad Request
   404 Not Found
   204 No Content
   ```

4. **Not validating request bodies**

   Never trust client input.

   Bad data can cause bugs, security issues, and broken database records.

5. **Confusing `PUT` and `PATCH`**

   `PUT` usually means replace the full resource.

   `PATCH` usually means update part of the resource.

6. **Making `GET` change data**

   Avoid designs like:

   ```text
   GET /todos/123/complete
   ```

   This changes server state and should not be a `GET`.

   Prefer:

   ```text
   PATCH /todos/123
   ```

   With body:

   ```json
   {
     "completed": true
   }
   ```

7. **Ignoring idempotency**

   Distributed systems have retries, timeouts, and duplicate requests.

   If repeated requests cause bad side effects, your API may fail in production.

8. **Poor error response design**

   Avoid vague errors:

   ```json
   {
     "error": "bad"
   }
   ```

   Prefer useful errors:

   ```json
   {
     "error": "validation_failed",
     "message": "title must not be empty"
   }
   ```

9. **Forgetting authorization**

   Finding a todo by ID is not enough.

   The API must also verify that the current user is allowed to access it.

10. **Not thinking about pagination**

   A list endpoint may work with 10 todos, but fail with 10 million.

   Production list endpoints usually need pagination, filtering, and sorting.

## Related Concepts

- HTTP methods
- HTTP status codes
- Request and response headers
- JSON request bodies
- Resource modeling
- URL design
- Idempotency
- Safe HTTP methods
- Request validation
- Authentication
- Authorization
- Pagination
- API versioning
- Error handling
- OpenAPI specifications
- Rate limiting
- Caching
- Observability
- Backward compatibility

## Interview-Level Explanation

REST API design models application data as resources and exposes those resources through HTTP methods.

For example, in a todo app, `/todos` represents the todo collection and `/todos/{id}` represents a single todo. `GET` reads resources, `POST` creates resources, `PATCH` updates part of a resource, and `DELETE` removes a resource.

Good REST APIs use meaningful status codes like `201 Created`, `400 Bad Request`, `404 Not Found`, and `204 No Content`. They validate input, return clear errors, protect resources with authorization, and consider idempotency so retries do not cause unintended side effects.

## Hands-On Exercise

Design REST endpoints for a todo app.

Your app must support:

- Create todo
- List todos
- Update todo
- Delete todo

### Step 1: Define the Resource

Decide what your main resource is.

For this exercise:

```text
todos
```

Collection URL:

```text
/todos
```

Single resource URL:

```text
/todos/{todoId}
```

### Step 2: Define the Todo Shape

Write an example todo object.

Example:

```json
{
  "id": "todo_123",
  "title": "Practice REST API design",
  "completed": false,
  "createdAt": "2026-05-03T10:00:00Z",
  "updatedAt": "2026-05-03T10:00:00Z"
}
```

### Step 3: Design the Create Endpoint

Define:

```text
POST /todos
```

Request body:

```json
{
  "title": "Practice REST API design"
}
```

Success response:

```text
201 Created
```

Response body:

```json
{
  "id": "todo_123",
  "title": "Practice REST API design",
  "completed": false,
  "createdAt": "2026-05-03T10:00:00Z",
  "updatedAt": "2026-05-03T10:00:00Z"
}
```

Validation rules:

- `title` is required
- `title` must be a string
- `title` must not be empty

Validation error:

```text
400 Bad Request
```

```json
{
  "error": "validation_failed",
  "message": "title must not be empty"
}
```

### Step 4: Design the List Endpoint

Define:

```text
GET /todos
```

Success response:

```text
200 OK
```

Response body:

```json
{
  "items": [
    {
      "id": "todo_123",
      "title": "Practice REST API design",
      "completed": false,
      "createdAt": "2026-05-03T10:00:00Z",
      "updatedAt": "2026-05-03T10:00:00Z"
    }
  ]
}
```

Optional query parameters:

```text
GET /todos?completed=false&limit=20
```

Think about:

- How would you filter completed todos?
- How would you limit the number of results?
- What happens if there are no todos?

A valid empty response can be:

```json
{
  "items": []
}
```

### Step 5: Design the Update Endpoint

Use `PATCH` for partial updates.

Define:

```text
PATCH /todos/{todoId}
```

Request body example:

```json
{
  "completed": true
}
```

Success response:

```text
200 OK
```

Response body:

```json
{
  "id": "todo_123",
  "title": "Practice REST API design",
  "completed": true,
  "createdAt": "2026-05-03T10:00:00Z",
  "updatedAt": "2026-05-03T10:10:00Z"
}
```

Validation rules:

- `title`, if present, must be a non-empty string
- `completed`, if present, must be a boolean
- At least one updatable field should be present

If the todo does not exist:

```text
404 Not Found
```

```json
{
  "error": "not_found",
  "message": "todo not found"
}
```

### Step 6: Design the Delete Endpoint

Define:

```text
DELETE /todos/{todoId}
```

Success response:

```text
204 No Content
```

No response body.

Think about idempotency:

- If the todo exists, delete it.
- If the same delete request is sent again, the final state is still “todo does not exist.”

You should decide whether the second delete returns:

```text
204 No Content
```

or:

```text
404 Not Found
```

Both designs exist. The important thing is to be consistent and document the behavior.

### Step 7: Write a Small API Table

Create a table like this:

| Operation | Method | Path | Success Status | Request Body | Response Body |
|---|---:|---|---:|---|---|
| Create todo | `POST` | `/todos` | `201` | Todo input | Created todo |
| List todos | `GET` | `/todos` | `200` | None | Todo list |
| Update todo | `PATCH` | `/todos/{todoId}` | `200` | Fields to update | Updated todo |
| Delete todo | `DELETE` | `/todos/{todoId}` | `204` | None | None |

### Step 8: Write Error Cases

Document at least these errors:

| Case | Status Code | Example |
|---|---:|---|
| Invalid title | `400` | Empty title |
| Todo not found | `404` | Unknown `todoId` |
| Invalid JSON | `400` | Malformed request body |
| Unauthorized user | `401` | Missing login token |
| Forbidden access | `403` | Todo belongs to another user |

### Step 9: Explain Idempotency

For each endpoint, answer whether it is idempotent.

| Endpoint | Idempotent? | Why |
|---|---:|---|
| `POST /todos` | Usually no | Repeating it may create multiple todos |
| `GET /todos` | Yes | Repeating it should not change data |
| `PATCH /todos/{id}` | Depends | Some patches are idempotent, some are not |
| `DELETE /todos/{id}` | Yes | Final state is deleted |

## Expected Outcome

After completing this exercise, you should be able to:

- Explain what a REST resource is
- Design resource-based URLs
- Choose correct HTTP methods for common CRUD actions
- Use appropriate status codes
- Define request and response bodies
- Validate request input
- Explain why `GET` should not modify data
- Explain idempotency in practical terms
- Design a basic todo API that another engineer could implement
- Describe how poor API design can cause production problems

## Quiz Questions

1. Why is `POST /todos` usually not idempotent, but `DELETE /todos/{id}` usually is?

2. What status code would you return when a client sends a create todo request with an empty `title`, and why?

3. Why is `GET /todos/123/complete` a poor REST API design?

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

Next, learn about **request and response validation** in backend APIs.

REST endpoint design decides what your API should look like. Validation decides how your API safely handles real client input, bad data, missing fields, wrong types, and error responses.
