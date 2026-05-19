# Day 020 — Incident Response Basics

Date: 2026-05-19

## Phase

Phase 4 — System Design and Production

## Learning Objective

By the end of this lesson, you should understand how engineering teams respond to production issues.

You should be able to explain:

- What incident severity means
- What an incident commander does
- How to build an incident timeline
- Why communication matters during outages
- How mitigation differs from root-cause fixing
- What a postmortem is and why teams write one

## Why This Topic Matters

Production systems fail.

APIs go down. Databases overload. Deployments break traffic. Cloud regions have problems. Certificates expire. Queues back up. DNS changes go wrong.

As a backend or platform engineer, your job is not only to build systems. Your job is also to help operate them safely.

Incident response matters because during a production issue:

- Users may be unable to use the product.
- Revenue may be affected.
- Engineers are under pressure.
- Bad communication can make the problem worse.
- Random debugging can waste valuable time.
- Teams need to restore service quickly and learn afterward.

Strong engineering teams do not rely on panic. They use a structured incident process.

The goal is not to blame someone.

The goal is:

1. Detect the issue.
2. Understand impact.
3. Coordinate response.
4. Mitigate quickly.
5. Communicate clearly.
6. Learn from the incident.
7. Prevent similar failures.

## Simple Explanation

An incident is a production problem that affects users or business operations.

Example:

> The public API is returning `500 Internal Server Error` for most requests.

When this happens, the team needs a plan.

A basic incident response process looks like this:

1. **Declare the incident**
   - Confirm that this is serious enough to treat as an incident.

2. **Assign roles**
   - Someone coordinates the response.
   - Someone investigates.
   - Someone communicates updates.

3. **Determine severity**
   - Is this a small bug?
   - Is the whole system down?
   - Are paying customers affected?

4. **Create a timeline**
   - Record what happened and when.

5. **Mitigate**
   - Restore service as quickly as possible.
   - This may mean rolling back, disabling a feature, scaling up, or routing traffic away.

6. **Communicate**
   - Keep internal teams and possibly customers updated.

7. **Write a postmortem**
   - After the incident, document what happened, why it happened, and how to improve.

A key idea:

> During an incident, restoring service comes before proving the perfect root cause.

You can investigate deeply after users are no longer affected.

## Real-World Analogy

Think of incident response like firefighters responding to a fire.

If a building is on fire, the first goal is not to write a detailed report about why the fire started.

The first goal is to:

1. Confirm there is an emergency.
2. Get the right people involved.
3. Assign someone to lead.
4. Stop the fire from spreading.
5. Protect people.
6. Communicate with others nearby.
7. Afterward, investigate the cause.
8. Improve prevention for next time.

Production incidents work similarly.

If an API outage is affecting users, the team should not spend two hours arguing about whose code caused it.

The team should first restore service.

Then, after the incident, they can analyze:

- What failed?
- Why did detection take so long?
- Why did mitigation take so long?
- What would prevent this in the future?

## Technical Explanation

Incident response is the operational process used to handle unexpected production failures.

A production incident usually includes these parts:

```text
Detection -> Triage -> Declaration -> Coordination -> Mitigation -> Resolution -> Postmortem
```

### 1. Detection

An incident can be detected by:

- Monitoring alerts
- Error-rate dashboards
- Latency dashboards
- Customer reports
- Synthetic checks
- Logs
- On-call engineer investigation

Example alert:

```text
High 5xx error rate on public API
Service: payments-api
Error rate: 38%
Threshold: > 5% for 5 minutes
Started: 14:03 UTC
```

Detection answers:

- What signal says something is wrong?
- When did the issue start?
- Which service is affected?
- How many users are affected?

### 2. Triage

Triage means quickly understanding the situation.

Questions to ask:

- Is this real or a false alarm?
- Is customer traffic affected?
- Is this one region or all regions?
- Is this one endpoint or the entire API?
- Did a recent deployment happen?
- Are dependencies healthy?
- Is there a known cloud/provider issue?

Triage should be fast. You do not need perfect knowledge yet.

### 3. Incident Declaration

When impact is serious enough, the team declares an incident.

Declaring an incident is useful because it tells everyone:

> This is no longer normal debugging. We are now using the incident process.

A declaration might look like:

```text
Incident declared at 14:08 UTC.

Summary:
Public API is returning elevated 500 errors across multiple endpoints.

Impact:
Approximately 45% of requests are failing for customers in us-east-1.

Severity:
SEV-1

Incident Commander:
Alex

Communication channel:
#inc-2026-05-19-api-outage
```

### 4. Severity

Severity describes business and user impact.

Every company defines severity differently, but a simple model is:

| Severity | Meaning | Example |
|---|---|---|
| SEV-1 | Critical production outage | API unavailable for most users |
| SEV-2 | Major degradation | Checkout failing for some users |
| SEV-3 | Minor production issue | One non-critical feature is broken |
| SEV-4 | Low-impact issue | Internal dashboard bug |

Severity is not about how interesting the bug is.

Severity is about impact.

A small code bug can be SEV-1 if it takes down the API.

A complex infrastructure problem can be SEV-3 if users barely notice it.

### 5. Incident Commander

The incident commander is the person coordinating the response.

The incident commander does not need to be the deepest technical expert.

Their job is to create order.

Responsibilities include:

- Keep the response organized.
- Assign tasks.
- Make sure people are not duplicating work.
- Ask for status updates.
- Track the timeline.
- Decide when to escalate.
- Decide when the incident is mitigated or resolved.
- Ensure communication happens.

During an incident, engineers often want to jump straight into debugging. That is understandable, but without coordination, five people may investigate the same thing while nobody communicates to stakeholders.

The incident commander prevents that.

### 6. Communication

Communication is part of incident response, not an optional extra.

There are usually two communication types:

#### Internal communication

For engineering, support, management, and operations.

Example:

```text
14:15 UTC Update:
We have confirmed elevated 500s on the public API.
Impact is currently limited to us-east-1.
Current hypothesis: bad deployment to api-service version 2026.05.19.3.
Next action: rolling back to version 2026.05.19.2.
Next update in 10 minutes.
```

#### External communication

For customers or users, often through a status page or customer support.

Example:

```text
We are investigating elevated error rates affecting API requests.
Some customers may see failed requests or increased latency.
We will provide another update in 15 minutes.
```

Good communication should include:

- What is affected
- What users may experience
- What the team is doing
- When the next update will happen

Avoid saying things that are not confirmed.

Bad:

```text
Database is definitely broken.
```

Better:

```text
We are investigating database connection errors as a possible cause.
```

### 7. Mitigation vs. Root Cause

This is one of the most important incident response concepts.

#### Mitigation

Mitigation means reducing or stopping user impact.

Examples:

- Roll back a deployment.
- Disable a broken feature flag.
- Scale up service replicas.
- Restart unhealthy workers.
- Route traffic to another region.
- Increase queue consumers.
- Temporarily block expensive requests.
- Restore from backup.
- Fail over to a replica.

Mitigation answers:

> How do we make the service work again?

#### Root cause

Root cause analysis happens after or near the end of the incident.

It answers:

> Why did this happen?

Example:

```text
Mitigation:
Rolled back api-service from v3 to v2.

Root cause:
v3 introduced a database query that caused connection pool exhaustion under production traffic.
```

During an active outage, do not get stuck trying to prove every detail if a safe rollback can restore service.

### 8. Timeline

A timeline is a timestamped record of important events.

It helps the team understand what happened.

Example:

```text
14:03 - Alert fired: API 5xx error rate above 5%.
14:05 - On-call engineer acknowledged alert.
14:08 - Incident declared as SEV-1.
14:09 - Incident channel created.
14:10 - Incident commander assigned.
14:12 - Error rate confirmed at 42% in us-east-1.
14:15 - Recent deployment identified: api-service v2026.05.19.3.
14:18 - Rollback started.
14:24 - Rollback completed.
14:27 - Error rate dropped below 2%.
14:35 - Monitoring stable for 10 minutes.
14:38 - Incident marked mitigated.
15:30 - Postmortem scheduled.
```

A good timeline includes:

- Alerts
- Decisions
- Actions
- Deployments
- Rollbacks
- Customer impact changes
- Communication updates
- Resolution time

### 9. Resolution

An incident can have different end states:

#### Mitigated

User impact has stopped or reduced to an acceptable level, but the root cause may still need investigation.

#### Resolved

The issue is fully fixed, and the system is stable.

Many teams first mark an incident as mitigated, then resolved later.

Example:

```text
14:38 - Incident mitigated. API error rate has returned to normal after rollback.
16:10 - Incident resolved. Root cause confirmed and unsafe deployment blocked.
```

### 10. Postmortem

A postmortem is a written review after the incident.

A good postmortem is blameless.

That means it focuses on systems, processes, and decisions — not personal blame.

A postmortem usually includes:

- Summary
- Impact
- Timeline
- Root cause
- Detection
- Response
- What went well
- What went poorly
- Action items
- Owners and due dates

Example action items:

```text
- Add load test for database-heavy API queries.
  Owner: Backend Team
  Due: 2026-06-01

- Add alert for database connection pool saturation.
  Owner: Platform Team
  Due: 2026-05-26

- Improve deployment dashboard to show recent releases by service.
  Owner: Developer Experience Team
  Due: 2026-06-10
```

Weak action item:

```text
Be more careful next time.
```

Strong action item:

```text
Require automated query performance checks before deploying changes to /v1/orders/search.
```

## Practical Example

Imagine you operate this simple backend system:

```text
Users
  |
  v
Load Balancer
  |
  v
api-service
  |
  +--> PostgreSQL
  |
  +--> Redis
```

At 14:03 UTC, your alert fires:

```text
ALERT: High API 5xx Error Rate

Service: api-service
Environment: production
Region: us-east-1
Current 5xx rate: 41%
Threshold: 5%
Duration: 5 minutes
```

You check the health endpoint:

```bash
curl -i https://api.example.com/health
```

Response:

```http
HTTP/2 500
content-type: application/json

{
  "status": "unhealthy",
  "database": "connection_timeout",
  "redis": "ok"
}
```

You check a user-facing endpoint:

```bash
curl -i https://api.example.com/v1/orders
```

Response:

```http
HTTP/2 500
content-type: application/json

{
  "error": "internal_server_error",
  "request_id": "req_abc123"
}
```

You check recent deployments:

```text
14:00 UTC - api-service v2026.05.19.3 deployed to production
13:10 UTC - worker-service v2026.05.19.7 deployed to production
```

You check logs:

```text
2026-05-19T14:04:11Z ERROR request_id=req_abc123
message="database connection timeout"
endpoint="/v1/orders"
db_pool_wait_ms=5000
version="v2026.05.19.3"
```

You check database metrics:

```text
Database CPU: 72%
Active connections: 500/500
Connection pool saturation: 100%
Slow queries increased after 14:00 UTC
```

A reasonable incident response could be:

```text
14:08 - Declare SEV-1 incident.
14:09 - Assign incident commander.
14:10 - Create incident Slack/Teams channel.
14:12 - Confirm API is returning 500s for many customers.
14:15 - Identify recent api-service deployment.
14:18 - Start rollback to previous version.
14:24 - Rollback complete.
14:27 - API 5xx rate returns to normal.
14:38 - Incident mitigated after 10 minutes of stable metrics.
15:30 - Begin postmortem draft.
```

The mitigation is rollback.

The likely root cause is a bad deployment that created expensive database behavior.

But during the incident, the team should focus on restoring service first.

## Official Documentation To Read

- [Google SRE Book — Managing Incidents](https://sre.google/sre-book/managing-incidents/)

## Good Reads

- [Atlassian — Incident management](https://www.atlassian.com/incident-management)

## Where This Appears in Production

Incident response appears anywhere real users depend on software.

Common examples:

### API outages

An API starts returning errors or timing out.

Possible causes:

- Bad deployment
- Database overload
- Load balancer misconfiguration
- Dependency outage
- Authentication failure
- Cloud networking issue

### Database incidents

A database becomes slow, unavailable, or overloaded.

Possible causes:

- Bad query
- Missing index
- Lock contention
- Disk full
- Connection pool exhaustion
- Failover problem

### Queue backlogs

Asynchronous jobs stop processing fast enough.

Possible causes:

- Worker crash loop
- Poison message
- Traffic spike
- Downstream dependency failure
- Insufficient consumers

### Deployment incidents

A release breaks production.

Possible causes:

- Missing environment variable
- Bad migration
- Incompatible API change
- Broken container image
- Feature flag misconfiguration

### Infrastructure incidents

Platform components fail.

Possible causes:

- Kubernetes node failures
- DNS issues
- Certificate expiration
- Cloud region problems
- Network policy mistakes
- Autoscaling failures

### Security incidents

Suspicious or confirmed unauthorized access occurs.

Possible causes:

- Credential leak
- Misconfigured permissions
- Vulnerable dependency
- Compromised token
- Publicly exposed internal service

Security incidents often have a different response process, but they still require clear ownership, timeline, communication, and post-incident review.

## Common Beginner Mistakes

### 1. Debugging without declaring an incident

Beginners may keep investigating silently while users are affected.

If impact is serious, declare the incident early.

Declaring does not mean you fully understand the problem. It means the team needs coordination.

### 2. Confusing severity with technical complexity

A simple bug can be severe if it affects many users.

A complex bug can be low severity if there is little or no customer impact.

Severity is about impact.

### 3. No clear incident commander

Without an incident commander, everyone may investigate randomly.

This causes:

- Duplicate work
- Missed communication
- Slow decisions
- Confusing updates

### 4. Poor timeline discipline

If nobody records what happened, the postmortem becomes guesswork.

Write down important events as they happen.

### 5. Waiting too long to communicate

Silence creates confusion.

Even if you do not know the cause, you can communicate:

```text
We are investigating elevated API error rates.
Next update in 15 minutes.
```

### 6. Trying to find perfect root cause before mitigation

If rollback is safe and likely to restore service, do it.

Deep analysis can happen after impact is reduced.

### 7. Blaming individuals in the postmortem

Bad postmortem:

```text
The outage happened because Sam deployed bad code.
```

Better postmortem:

```text
The deployment pipeline allowed a database-heavy query change to reach production without load testing or query performance checks.
```

The second version helps the system improve.

### 8. Writing vague action items

Bad:

```text
Improve monitoring.
```

Better:

```text
Add alert when api-service database connection pool usage exceeds 85% for 5 minutes.
```

### 9. Not defining incident roles

Common roles include:

- Incident commander
- Technical lead
- Communications lead
- Scribe/timeline owner
- Subject matter experts

Small teams may combine roles, but the responsibilities still need to be covered.

### 10. Declaring victory too early

If metrics improve for one minute, that may not be enough.

Watch the system for stability before marking the incident mitigated or resolved.

## Related Concepts

- On-call engineering
- Service-level objectives, or SLOs
- Service-level indicators, or SLIs
- Error budgets
- Monitoring and alerting
- Logs, metrics, and traces
- Runbooks
- Playbooks
- Rollbacks
- Feature flags
- Canary deployments
- Blue-green deployments
- Disaster recovery
- High availability
- Load balancing
- Rate limiting
- Circuit breakers
- Postmortems
- Blameless culture
- Change management
- Escalation policies
- Status pages

## Interview-Level Explanation

Incident response is the structured process teams use to handle production failures.

A good response starts by detecting and triaging the issue, then declaring an incident if user impact is significant. The team assigns an incident commander, determines severity, coordinates investigation, communicates status, and focuses first on mitigation to restore service. After the incident, the team writes a blameless postmortem with a timeline, root cause analysis, lessons learned, and concrete action items to reduce the chance or impact of similar incidents in the future.

## Hands-On Exercise

Write a mock incident timeline for an API outage.

Use this scenario:

```text
Your company runs a public REST API.

At 09:00 UTC, a new version of the API service is deployed.
At 09:07 UTC, alerts show elevated 5xx errors.
Customers report that requests to /v1/payments are failing.
The database is healthy, but logs show a new application exception.
A rollback restores the API.
```

### Step 1: Define the incident summary

Write a short summary.

Example format:

```text
Incident Summary:
The public API experienced elevated 500 errors on /v1/payments after a production deployment. The issue affected payment creation requests for customers until the API service was rolled back.
```

### Step 2: Assign severity

Choose a severity.

Use this simple model:

```text
SEV-1: Critical outage affecting most users or critical business flow
SEV-2: Major degradation affecting important functionality
SEV-3: Minor user-facing issue
SEV-4: Low-impact or internal issue
```

For this scenario, `SEV-1` or `SEV-2` may be reasonable depending on how important payments are.

Write your decision and explain why.

Example:

```text
Severity:
SEV-1

Reason:
The /v1/payments endpoint is a critical business flow, and customers were unable to create payments.
```

### Step 3: Assign incident roles

Choose names or placeholders.

Example:

```text
Incident Commander: Priya
Technical Lead: Marcus
Communications Lead: Elena
Scribe: Jordan
```

Then explain what each person does.

### Step 4: Write the timeline

Create a timestamped timeline.

Use UTC.

Example:

```text
09:00 - api-service v2026.05.19.1 deployed to production.
09:07 - Alert fired for elevated 5xx error rate.
09:08 - On-call engineer acknowledged alert.
09:10 - Customer support reported payment failures.
09:11 - Incident declared as SEV-1.
09:12 - Incident channel created.
09:13 - Incident commander assigned.
09:15 - Technical investigation began.
09:18 - Logs showed application exceptions on /v1/payments.
09:20 - Database health checked and confirmed normal.
09:22 - Recent deployment identified as likely trigger.
09:24 - Decision made to roll back api-service.
09:26 - Rollback started.
09:31 - Rollback completed.
09:34 - 5xx error rate returned to normal.
09:45 - System stable for 10 minutes.
09:46 - Incident marked mitigated.
10:30 - Postmortem draft started.
```

### Step 5: Write internal updates

Create at least three internal updates.

Example:

```text
09:15 Update:
We have declared a SEV-1 incident for elevated 500 errors on /v1/payments. Investigation is focused on the api-service. Next update in 10 minutes.

09:25 Update:
Recent api-service deployment is the current leading suspect. Database health appears normal. We are starting rollback now. Next update in 10 minutes.

09:45 Update:
Rollback completed and API error rate has returned to normal. We are monitoring for stability before marking the incident mitigated.
```

### Step 6: Write customer-facing updates

Create two or three short customer-facing messages.

Example:

```text
Investigating:
We are investigating elevated error rates affecting payment API requests. Some customers may see failed requests.

Update:
We have identified a likely cause and are rolling back a recent API change.

Resolved:
Payment API error rates have returned to normal. We are continuing to monitor the system.
```

### Step 7: Describe mitigation

Write what the team did to reduce user impact.

Example:

```text
Mitigation:
The team rolled back api-service from v2026.05.19.1 to the previous stable version. After rollback, /v1/payments error rates returned to normal.
```

### Step 8: Draft postmortem notes

Write a short postmortem draft with these sections:

```text
Title:

Date:

Severity:

Impact:

Root Cause:

Detection:

Timeline:

What Went Well:

What Went Poorly:

Action Items:
```

Example action items:

```text
1. Add automated integration test for /v1/payments error handling.
   Owner: Backend Team
   Due: 2026-05-26

2. Add deployment dashboard annotation to API error-rate graphs.
   Owner: Platform Team
   Due: 2026-05-28

3. Add alert for endpoint-specific 5xx error rate on /v1/payments.
   Owner: Observability Team
   Due: 2026-05-30
```

### Step 9: Review your incident response

Check your work against these questions:

- Did you define severity?
- Did you name an incident commander?
- Did you include a clear timeline?
- Did you separate internal and external communication?
- Did you describe mitigation?
- Did you include a postmortem?
- Did your action items have owners?
- Did your action items have due dates?
- Did you avoid blaming individuals?

## Expected Outcome

After completing this exercise, you should be able to explain and produce the basic parts of an incident response.

You should be able to write:

- A clear incident summary
- A severity classification
- Incident roles, especially incident commander
- A timestamped incident timeline
- Internal engineering updates
- Customer-facing updates
- A mitigation description
- A basic postmortem
- Concrete follow-up action items

You should also understand the difference between:

```text
Mitigation: restoring service or reducing user impact
Root cause: explaining why the incident happened
Postmortem: documenting what happened and how to improve
```

## Quiz Questions

1. What is the difference between mitigation and root cause analysis during an incident?

2. Why is an incident commander useful during a production outage?

3. What should be included in a good incident timeline?

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

The next logical topic is **postmortems and reliability improvement**.

Incident response teaches you how teams handle production failures while they are happening. The next step is learning how teams turn incidents into long-term reliability improvements through blameless postmortems, action items, better monitoring, safer deployments, and stronger system design.
