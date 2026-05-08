# Day 009 — Authentication vs Authorization

Date: 2026-05-08

## Phase

Phase 1 — Backend Foundations

## Learning Objective

By the end of this lesson, you should understand the difference between:

- **Authentication**: proving who a user or service is.
- **Authorization**: checking what that user or service is allowed to do.

You should also be able to explain the relationship between:

- Login
- Identity
- Sessions
- Tokens
- Roles
- Permissions
- Least privilege

## Why This Topic Matters

Authentication and authorization are core parts of almost every backend system.

In production systems, you need to answer two different questions:

1. **Who is making this request?**
2. **Is this requester allowed to perform this action?**

If you confuse these, serious security bugs can happen.

Examples:

- A user logs in successfully but can access another user's private data.
- An editor can delete admin-only resources.
- A backend service accepts a token but never checks whether the token has the right permission.
- An API endpoint hides a button in the frontend but still allows unauthorized requests directly.

In real backend, platform, and cloud systems, authentication and authorization appear in:

- API gateways
- Web applications
- Admin dashboards
- Internal tools
- Kubernetes access control
- Cloud IAM systems
- Service-to-service communication
- CI/CD deployment permissions
- Database access policies

Security is not only about keeping attackers out. It is also about making sure authenticated users can only do what they are supposed to do.

## Simple Explanation

**Authentication** means proving identity.

Example:

> “I am Alice. Here is my password, passkey, or token to prove it.”

**Authorization** means checking permission.

Example:

> “Alice is logged in. Is Alice allowed to delete this project?”

They are related, but they are not the same.

A user can be authenticated but not authorized.

For example:

- You log in to a company system.
- The system knows you are you.
- But you still cannot access payroll records because you are not in the HR role.

So:

```text
Authentication = Who are you?
Authorization  = What are you allowed to do?
```

A typical request flow looks like this:

```text
User logs in
   ↓
System authenticates the user
   ↓
System creates a session or token
   ↓
User sends a request
   ↓
System identifies the user from session/token
   ↓
System checks authorization rules
   ↓
Request is allowed or denied
```

## Real-World Analogy

Think about entering an office building.

### Authentication

At the front desk, you show your ID badge.

The guard checks:

> “Are you really an employee?”

That is authentication.

### Authorization

After entering the building, you try to open different doors.

Your badge may open:

- The main entrance
- Your team office
- The kitchen

But it may not open:

- The server room
- The finance office
- The executive boardroom

That is authorization.

You are authenticated as an employee, but you are not authorized to access every room.

In backend systems, login is like showing your badge. Permissions are like deciding which doors your badge can open.

## Technical Explanation

Authentication and authorization are usually implemented as separate layers.

### Authentication

Authentication verifies identity.

Common authentication methods include:

- Username and password
- Multi-factor authentication
- Passkeys
- OAuth/OIDC login
- API keys
- Client certificates
- Service account credentials

After successful authentication, the system usually creates some proof that future requests can use.

Common examples:

- **Session ID stored in a cookie**
- **JWT access token**
- **Opaque bearer token**
- **API key**

Example:

```text
POST /login
username=alice
password=correct-password

Response:
Set-Cookie: session_id=abc123
```

Now the user can make future requests with that session cookie.

### Identity

Identity is the information the system knows about the authenticated requester.

Example user identity:

```json
{
  "user_id": "user_123",
  "email": "alice@example.com",
  "name": "Alice",
  "roles": ["editor"]
}
```

For service-to-service systems, identity may represent a service instead of a human:

```json
{
  "service": "billing-service",
  "environment": "production"
}
```

### Sessions

A session is server-side state that remembers a logged-in user.

Example:

```text
Browser stores:
session_id=abc123

Server stores:
abc123 → user_id=user_123
```

When the browser sends `session_id=abc123`, the server looks up the session and knows the request is from `user_123`.

Sessions are common in traditional web applications.

### Tokens

A token is a credential sent with requests to prove authentication.

Example HTTP request:

```http
GET /api/articles
Authorization: Bearer eyJhbGciOi...
```

Tokens are common in APIs, mobile apps, single-page apps, and service-to-service systems.

Important: accepting a valid token only proves authentication. You still need authorization checks.

A token might say:

```json
{
  "sub": "user_123",
  "roles": ["editor"],
  "exp": 1778265600
}
```

The backend should still check:

```text
Is user_123 allowed to perform this action on this resource?
```

### Authorization

Authorization decides whether an authenticated identity can perform an action.

A basic authorization check usually combines:

```text
subject + action + resource
```

Example:

```text
Subject: user_123
Action: delete
Resource: article_789
```

The system asks:

> Is `user_123` allowed to `delete` `article_789`?

Authorization can be implemented using:

- Roles
- Permissions
- Access control lists
- Attribute-based rules
- Ownership checks
- Policy engines

### Roles

A role is a named group of permissions.

Example roles:

- `admin`
- `editor`
- `viewer`

Instead of assigning many permissions to every user individually, you assign users to roles.

Example:

```json
{
  "user_id": "user_123",
  "roles": ["editor"]
}
```

### Permissions

A permission is a specific allowed action.

Examples:

```text
article:read
article:create
article:update
article:delete
user:manage
billing:read
```

Roles usually contain permissions.

Example:

```json
{
  "admin": [
    "article:read",
    "article:create",
    "article:update",
    "article:delete",
    "user:manage"
  ],
  "editor": [
    "article:read",
    "article:create",
    "article:update"
  ],
  "viewer": [
    "article:read"
  ]
}
```

### Least Privilege

Least privilege means giving each user or service only the permissions they need, and nothing more.

For example:

- A viewer should not be able to edit articles.
- An editor should not be able to manage users.
- A CI/CD job that deploys one service should not have full cloud admin access.
- A read-only monitoring service should not have database write access.

Least privilege limits damage when accounts, tokens, or services are compromised.

## Practical Example

Imagine a simple article management API.

There are three roles:

- `admin`
- `editor`
- `viewer`

You need to protect these API endpoints:

```text
GET    /articles          Read articles
POST   /articles          Create an article
PATCH  /articles/:id      Update an article
DELETE /articles/:id      Delete an article
GET    /users             View users
PATCH  /users/:id/role    Change user roles
```

A simple permission matrix could look like this:

| Action | Admin | Editor | Viewer |
|---|---:|---:|---:|
| Read articles | Yes | Yes | Yes |
| Create articles | Yes | Yes | No |
| Update articles | Yes | Yes | No |
| Delete articles | Yes | No | No |
| View users | Yes | No | No |
| Change user roles | Yes | No | No |

In code, that could be represented like this:

```js
const rolePermissions = {
  admin: [
    "article:read",
    "article:create",
    "article:update",
    "article:delete",
    "user:read",
    "user:change_role"
  ],
  editor: [
    "article:read",
    "article:create",
    "article:update"
  ],
  viewer: [
    "article:read"
  ]
};

function hasPermission(user, permission) {
  return user.roles.some((role) => {
    const permissions = rolePermissions[role] || [];
    return permissions.includes(permission);
  });
}

// Example authenticated user
const user = {
  id: "user_123",
  email: "alice@example.com",
  roles: ["editor"]
};

// Authorization check
if (!hasPermission(user, "article:delete")) {
  console.log("403 Forbidden");
} else {
  console.log("Article deleted");
}
```

Output:

```text
403 Forbidden
```

Why?

Because Alice is authenticated, and the system knows she is an editor. But editors do not have the `article:delete` permission.

A backend route might look conceptually like this:

```js
app.delete("/articles/:id", authenticateUser, (req, res) => {
  const user = req.user;

  if (!hasPermission(user, "article:delete")) {
    return res.status(403).json({
      error: "Forbidden"
    });
  }

  // Delete article here
  return res.status(204).send();
});
```

Important distinction:

```text
401 Unauthorized = You are not authenticated.
403 Forbidden    = You are authenticated, but not allowed.
```

The names are slightly confusing because `401 Unauthorized` sounds like authorization, but in HTTP practice it usually means authentication is missing or invalid.

Example:

```text
No token or invalid token:
→ 401 Unauthorized

Valid token but missing permission:
→ 403 Forbidden
```

## Official Documentation To Read

- [OWASP — Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [OWASP — Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)

## Good Reads

- [Auth0 — Authentication vs Authorization](https://auth0.com/docs/get-started/identity-fundamentals/authentication-and-authorization)

## Where This Appears in Production

Authentication and authorization appear almost everywhere in production systems.

### Web Applications

A user logs in with email and password.

Then the backend checks whether the user can:

- View a page
- Create a resource
- Edit a resource
- Delete a resource
- Access an admin panel

### APIs

APIs often use bearer tokens.

Example:

```bash
curl https://api.example.com/articles \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

The backend must validate the token and then check permissions.

### Admin Dashboards

Admin dashboards are high-risk because they often control users, billing, content, or infrastructure.

A common production mistake is allowing any logged-in employee to access admin actions.

Good systems separate roles such as:

- Support agent
- Billing admin
- Content moderator
- Super admin

### Microservices

Services also need identity and permissions.

Example:

```text
checkout-service calls payment-service
```

The payment service should know:

- Is the caller really `checkout-service`?
- Is `checkout-service` allowed to create payment intents?
- Is it allowed to issue refunds?

### Cloud and Platform Engineering

Cloud IAM systems are authorization systems.

Examples of access decisions:

- Can this user create a database?
- Can this service account read from this storage bucket?
- Can this CI/CD pipeline deploy to production?
- Can this Kubernetes service account list secrets?

### Observability and Audit Logs

Security-sensitive systems should log authorization decisions.

Example log:

```json
{
  "event": "authorization_denied",
  "user_id": "user_123",
  "action": "user:change_role",
  "resource": "user_456",
  "reason": "missing_permission",
  "timestamp": "2026-05-08T10:15:00Z"
}
```

These logs help with:

- Debugging access problems
- Detecting suspicious behavior
- Security audits
- Incident response

## Common Beginner Mistakes

1. **Thinking login is enough**

   Login only proves identity. You still need permission checks on protected actions.

2. **Only hiding buttons in the frontend**

   Hiding a “Delete” button is not security. Attackers can still call the API directly.

   Authorization must happen on the backend.

3. **Confusing roles and permissions**

   A role is a group.

   A permission is a specific allowed action.

   Example:

   ```text
   Role: editor
   Permissions: article:read, article:create, article:update
   ```

4. **Giving too many users admin access**

   This violates least privilege.

   Admin access should be rare, intentional, and auditable.

5. **Not checking resource ownership**

   This is a common bug.

   Example:

   ```text
   GET /users/123/orders
   ```

   The backend must check whether the authenticated user is allowed to view user `123`'s orders.

   It is not enough to check that the user is logged in.

6. **Trusting user-provided role fields**

   Never trust a request body like this:

   ```json
   {
     "role": "admin"
   }
   ```

   unless the authenticated requester is authorized to assign that role.

7. **Putting authorization only in one endpoint but forgetting others**

   For example, protecting:

   ```text
   DELETE /articles/:id
   ```

   but forgetting to protect:

   ```text
   PATCH /articles/:id
   ```

8. **Not distinguishing 401 and 403**

   Use:

   ```text
   401 = not authenticated
   403 = authenticated but not allowed
   ```

9. **Long-lived tokens with too much access**

   If a powerful token is stolen, the damage can be large.

   Use short expiration, rotation, scoped permissions, and least privilege.

10. **No audit trail**

   If someone changes permissions or accesses sensitive data, production systems should record who did it and when.

## Related Concepts

- Identity
- Login
- Password hashing
- Multi-factor authentication
- Sessions
- Cookies
- JWTs
- Bearer tokens
- API keys
- OAuth
- OpenID Connect
- Role-based access control
- Attribute-based access control
- Access control lists
- Least privilege
- Service accounts
- Cloud IAM
- Kubernetes RBAC
- Secret management
- Audit logging
- 401 Unauthorized
- 403 Forbidden

## Interview-Level Explanation

Authentication verifies identity: it answers, “Who are you?”

Authorization checks permissions: it answers, “What are you allowed to do?”

A user can be authenticated but still not authorized for a specific action. In a backend system, authentication usually happens through sessions, tokens, API keys, or similar credentials. Authorization should be enforced on the server for every protected resource or action, using roles, permissions, ownership checks, or policies. Good systems follow least privilege so users and services only get the access they actually need.

## Hands-On Exercise

Design a simple permission matrix for three roles:

- `admin`
- `editor`
- `viewer`

Use a simple content management system as the example.

### Step 1: Define the resources

Start with these resources:

```text
Article
User
Settings
```

### Step 2: Define the actions

Use these actions:

```text
read
create
update
delete
manage_roles
update_settings
```

### Step 3: Create permission names

Write permissions in this format:

```text
resource:action
```

Examples:

```text
article:read
article:create
article:update
article:delete
user:read
user:manage_roles
settings:update
```

### Step 4: Build a permission matrix

Fill in this table:

| Permission | Admin | Editor | Viewer |
|---|---:|---:|---:|
| article:read |  |  |  |
| article:create |  |  |  |
| article:update |  |  |  |
| article:delete |  |  |  |
| user:read |  |  |  |
| user:manage_roles |  |  |  |
| settings:update |  |  |  |

Use `Yes` or `No`.

### Step 5: Apply least privilege

Ask yourself:

- Does a viewer really need this permission?
- Does an editor really need this permission?
- Should only admins have this permission?
- Could this permission cause damage if abused?

### Step 6: Write role definitions

Convert your matrix into a structure like this:

```json
{
  "admin": [],
  "editor": [],
  "viewer": []
}
```

Example:

```json
{
  "admin": [
    "article:read",
    "article:create"
  ],
  "editor": [
    "article:read"
  ],
  "viewer": [
    "article:read"
  ]
}
```

Fill in the full permissions yourself.

### Step 7: Write three access decisions

Write the expected result for these cases:

```text
1. Viewer tries to delete an article.
2. Editor tries to update an article.
3. Editor tries to manage user roles.
```

For each case, answer:

```text
Authenticated? Yes/No
Authorized? Yes/No
Expected HTTP status: 200, 401, or 403
Reason:
```

### Step 8: Add one ownership rule

Add this rule:

```text
Editors can update only articles they created.
```

Now answer:

```text
Editor Alice created article_123.
Editor Bob created article_456.

Can Alice update article_123?
Can Alice update article_456?
Can Bob update article_456?
```

This shows that roles are sometimes not enough. You may also need resource-level authorization.

## Expected Outcome

After completing the exercise, you should be able to:

- Explain the difference between authentication and authorization.
- Describe what happens during login.
- Explain how sessions and tokens help identify future requests.
- Define roles and permissions.
- Build a simple role-to-permission matrix.
- Apply least privilege when assigning permissions.
- Explain why backend authorization checks are required.
- Distinguish between `401 Unauthorized` and `403 Forbidden`.
- Recognize when resource ownership checks are needed.

You should be able to say:

> Authentication proves who the requester is. Authorization checks whether that requester can perform a specific action on a specific resource.

## Quiz Questions

1. A user logs in successfully but gets blocked from deleting another user's account. Is this an authentication failure or an authorization failure?

2. What is the difference between a role and a permission?

3. Why is hiding an admin button in the frontend not enough to protect an admin API endpoint?

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

Next, learn about **password storage and password hashing**.

Authentication often starts with login, and login commonly involves passwords. The important backend concept is that you should not store raw passwords. You should store strong password hashes using purpose-built algorithms and safe password-handling practices.
