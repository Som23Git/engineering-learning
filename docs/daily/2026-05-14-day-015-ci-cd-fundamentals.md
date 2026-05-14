# Day 015 — CI/CD Fundamentals

Date: 2026-05-14

## Phase

Phase 2 — Containers and Platform

## Learning Objective

By the end of this lesson, you should understand how teams automate software delivery workflows using CI/CD.

You should be able to explain:

- What a pipeline is
- What jobs and steps are
- What runners do
- How automated tests run on every push
- What artifacts are
- How secrets are used safely
- What deployment gates are
- Why CI/CD is important for backend, platform, and production engineering

## Why This Topic Matters

In real production engineering, teams do not manually build, test, and deploy software from a developer laptop.

Manual delivery is risky because:

- People forget steps.
- Different engineers run different commands.
- Tests may be skipped.
- Broken code can reach production.
- Deployments become slow and stressful.
- Rollbacks become harder.

CI/CD helps teams make software delivery repeatable.

For backend and platform teams, CI/CD is the bridge between writing code and safely running that code in production.

A typical production workflow may look like this:

```text
Developer pushes code
        ↓
CI pipeline starts
        ↓
Install dependencies
        ↓
Run tests
        ↓
Build application or container image
        ↓
Scan or validate
        ↓
Deploy to staging
        ↓
Manual approval or automated checks
        ↓
Deploy to production
```

Without CI/CD, every release depends heavily on human memory.

With CI/CD, the delivery process is encoded as version-controlled configuration.

## Simple Explanation

CI/CD means automating the steps needed to safely deliver software.

CI means **Continuous Integration**.

It answers:

> “When someone changes code, does the project still build and do the tests still pass?”

CD can mean **Continuous Delivery** or **Continuous Deployment**.

Continuous Delivery means:

> “The software is always in a deployable state, but a human may still approve production deployment.”

Continuous Deployment means:

> “If all checks pass, the software is automatically deployed.”

A CI/CD pipeline is like a checklist that runs automatically.

For example, when you push code to GitHub, GitHub Actions can automatically:

1. Download your code.
2. Install dependencies.
3. Run tests.
4. Build the application.
5. Save test reports or build files.
6. Deploy the application if rules allow it.

The main idea is:

> Do the same important checks every time, automatically.

## Real-World Analogy

Think of CI/CD like an airport security and boarding process.

Before a plane can take off:

1. Passengers check in.
2. Bags are scanned.
3. IDs are verified.
4. The plane is inspected.
5. Boarding happens at the correct gate.
6. Final approval is given before takeoff.

Nobody wants the pilot to say:

> “I think we checked everything manually. Let’s hope.”

Software delivery works the same way.

Before code reaches production:

1. The code is checked out.
2. Dependencies are installed.
3. Tests are run.
4. Builds are created.
5. Security or quality checks may run.
6. Deployment may require approval.
7. Production release happens only after required gates pass.

CI/CD gives your software a reliable pre-flight checklist.

## Technical Explanation

A CI/CD system runs automated workflows based on events.

In GitHub Actions, the main pieces are:

```text
Event
  ↓
Workflow
  ↓
Jobs
  ↓
Steps
  ↓
Commands or Actions
  ↓
Runner executes them
```

### Event

An event is something that happens in GitHub.

Examples:

- A push to a branch
- A pull request opened
- A tag created
- A manual workflow dispatch
- A scheduled time

For this lesson, the important event is:

```yaml
on: push
```

That means:

> Run this workflow every time code is pushed.

### Workflow

A workflow is an automated process defined in a YAML file.

GitHub Actions workflows live in:

```text
.github/workflows/
```

Example:

```text
.github/workflows/test.yml
```

A repository can have many workflows.

For example:

```text
.github/workflows/test.yml
.github/workflows/build.yml
.github/workflows/deploy-staging.yml
.github/workflows/deploy-production.yml
```

### Job

A job is a group of steps that run on the same runner.

Example jobs:

- `test`
- `build`
- `lint`
- `deploy`

Jobs can run:

- In parallel by default
- In sequence if dependencies are defined with `needs`

Example:

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: echo "Run tests"

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - run: echo "Build app"
```

Here, `build` waits for `test` to finish successfully.

### Step

A step is one action inside a job.

A step can:

- Run a shell command
- Use a prebuilt GitHub Action

Example shell command step:

```yaml
- name: Run tests
  run: npm test
```

Example action step:

```yaml
- name: Check out repository
  uses: actions/checkout@v4
```

### Runner

A runner is the machine that executes the workflow.

For example:

```yaml
runs-on: ubuntu-latest
```

This means GitHub provides a Linux machine to run the job.

Common runner types include:

```yaml
runs-on: ubuntu-latest
runs-on: windows-latest
runs-on: macos-latest
```

Teams can also use self-hosted runners, but as a beginner, start with GitHub-hosted runners.

### Artifact

An artifact is a file or directory produced by a workflow and saved after the job finishes.

Examples:

- Test reports
- Build output
- Coverage reports
- Compiled binaries
- Deployment packages

Artifacts are useful because the runner is temporary. When the job ends, the runner is usually destroyed.

If you want to keep something from the workflow, upload it as an artifact.

### Secret

A secret is a sensitive value stored securely in the CI/CD platform.

Examples:

- API tokens
- Cloud credentials
- Docker registry passwords
- Deployment keys
- Database passwords

You should not hardcode secrets in workflow files.

Bad:

```yaml
- run: deploy --token=my-real-token
```

Better:

```yaml
- run: deploy --token="${{ secrets.DEPLOY_TOKEN }}"
```

Secrets help keep sensitive data out of Git history.

### Deployment Gate

A deployment gate is a control that must pass before deployment continues.

Examples:

- Tests must pass.
- Build must succeed.
- Security scan must pass.
- Deployment requires manual approval.
- Only the `main` branch can deploy.
- Production deploys require a protected environment.

Deployment gates reduce the chance of bad code reaching production.

A simple deployment gate might be:

```text
Only deploy if:
- branch is main
- tests passed
- a reviewer approved production deployment
```

## Practical Example

Here is a simple GitHub Actions workflow that runs tests on every push.

This example assumes a Node.js project with:

```text
package.json
package-lock.json
src/
test/
```

Create this file:

```text
.github/workflows/test.yml
```

Add:

```yaml
name: Run Tests

on:
  push:

jobs:
  test:
    name: Test Application
    runs-on: ubuntu-latest

    steps:
      - name: Check out repository
        uses: actions/checkout@v4

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: "20"

      - name: Install dependencies
        run: npm ci

      - name: Run tests
        run: npm test
```

What this does:

```text
on: push
```

Runs the workflow every time someone pushes code.

```yaml
jobs:
  test:
```

Defines one job named `test`.

```yaml
runs-on: ubuntu-latest
```

Runs the job on a GitHub-hosted Ubuntu runner.

```yaml
uses: actions/checkout@v4
```

Downloads your repository code into the runner.

```yaml
uses: actions/setup-node@v4
```

Installs Node.js on the runner.

```yaml
run: npm ci
```

Installs dependencies in a clean, repeatable way using `package-lock.json`.

```yaml
run: npm test
```

Runs your test command.

A simple architecture view:

```text
GitHub Repository
      │
      │ push
      ▼
GitHub Actions Workflow
      │
      ▼
Ubuntu Runner
      │
      ├── checkout code
      ├── install Node.js
      ├── install dependencies
      └── run tests
              │
              ▼
        pass or fail result
```

If tests pass, the workflow is green.

If tests fail, the workflow is red.

That red result is useful. It tells the team:

> This code should not be trusted until the failure is fixed.

## Official Documentation To Read

- [GitHub Actions — Documentation](https://docs.github.com/actions)
- [GitHub Actions — Events that trigger workflows](https://docs.github.com/actions/using-workflows/events-that-trigger-workflows)

## Good Reads

- [GitHub Actions — Workflow syntax](https://docs.github.com/actions/using-workflows/workflow-syntax-for-github-actions)

## Where This Appears in Production

CI/CD appears anywhere teams need to ship software safely and repeatedly.

Common production examples:

### Backend Services

A backend API may have a pipeline like:

```text
push code
  ↓
run unit tests
  ↓
run integration tests
  ↓
build Docker image
  ↓
push image to registry
  ↓
deploy to Kubernetes staging
  ↓
run smoke tests
  ↓
deploy to production
```

### Kubernetes Deployments

From the previous lesson, you learned about Kubernetes Pods and Deployments.

CI/CD often connects directly to Kubernetes.

For example:

```text
GitHub Actions
  ↓
Build container image
  ↓
Push image to container registry
  ↓
Update Kubernetes Deployment
  ↓
New Pods start with new image
```

This is where containers, Kubernetes, and CI/CD connect.

The application does not magically appear in a cluster. A delivery system usually builds it, publishes it, and deploys it.

### Platform Engineering

Platform teams often build reusable CI/CD templates.

Instead of every service team writing pipelines from scratch, the platform team may provide:

- Standard test workflows
- Standard Docker build workflows
- Approved deployment workflows
- Secret management patterns
- Security scanning steps
- Deployment approval gates

This helps many teams ship software consistently.

### Infrastructure as Code

CI/CD is also used for infrastructure changes.

For example:

```text
pull request opened
  ↓
run terraform fmt
  ↓
run terraform validate
  ↓
run terraform plan
  ↓
human reviews plan
  ↓
merge
  ↓
apply infrastructure change
```

This allows infrastructure changes to go through review and automated checks just like application code.

### Observability and Reliability

CI/CD can publish deployment events to observability systems.

This helps answer questions like:

```text
Did error rates increase after the latest deployment?
Did latency change after version 1.8.2?
Which deployment introduced this bug?
```

Reliable systems need traceability between code changes and production behavior.

## Common Beginner Mistakes

### 1. Thinking CI/CD is only deployment

CI/CD is not only deployment.

CI often starts with:

- Build
- Test
- Lint
- Validate
- Package

Deployment may come later.

A test-only workflow is still useful CI.

### 2. Skipping tests because the app “runs locally”

Local success is not enough.

CI gives the team a shared source of truth.

If it passes only on your laptop but fails in CI, the team should investigate.

### 3. Hardcoding secrets in workflow files

Never put real credentials in YAML files.

Bad:

```yaml
env:
  AWS_SECRET_ACCESS_KEY: "real-secret-value"
```

Use encrypted secrets instead:

```yaml
env:
  AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

### 4. Not pinning or understanding action versions

This is common:

```yaml
uses: actions/checkout@v4
```

The `@v4` is the action version.

Beginners sometimes remove the version or use random examples without understanding them.

Action versions matter because workflows depend on external reusable code.

### 5. Making one giant job

This can become hard to debug:

```text
one job:
  install
  lint
  test
  build
  package
  deploy staging
  deploy production
```

Better pipelines often separate concerns:

```text
lint job
test job
build job
deploy job
```

This makes failures easier to locate.

### 6. Deploying every branch to production

Production deployments should usually be gated.

For example:

```text
feature branches → tests only
main branch → tests + build + staging deploy
production environment → approval required
```

### 7. Ignoring failed pipelines

A failed pipeline is a signal.

If the team gets used to ignoring red builds, CI loses value.

A healthy team treats the main branch as something that should stay green.

### 8. Assuming runners are permanent servers

GitHub-hosted runners are temporary.

Each workflow job usually starts on a fresh machine.

Do not assume files from previous runs still exist.

If you need to keep output, use artifacts.

### 9. Confusing jobs and steps

Simple distinction:

```text
Workflow = the full automation
Job = a group of steps on a runner
Step = one command or action inside a job
Runner = the machine executing the job
```

### 10. Running deployment before validation

A dangerous order:

```text
deploy
  ↓
test
```

A safer order:

```text
test
  ↓
build
  ↓
deploy
```

## Related Concepts

- Git
- Pull requests
- Branch protection
- Automated testing
- Unit tests
- Integration tests
- Build systems
- Container images
- Docker
- Kubernetes Deployments
- Artifact registries
- Secrets management
- Environment variables
- Deployment environments
- Manual approvals
- Rollbacks
- Release strategies
- Blue-green deployment
- Canary deployment
- Infrastructure as Code
- Observability
- Change management
- Software supply chain security

## Interview-Level Explanation

CI/CD automates the process of building, testing, and deploying software.

In GitHub Actions, a workflow is triggered by an event such as a push or pull request. The workflow contains jobs, and each job runs steps on a runner. Steps can execute shell commands or reusable actions. Pipelines often produce artifacts, use secrets for sensitive credentials, and include deployment gates such as required tests, branch rules, or manual approvals.

The main value of CI/CD is repeatability and safety. It helps teams catch problems earlier, reduce manual release errors, and deploy production changes more reliably.

## Hands-On Exercise

Create a GitHub Actions workflow that runs tests on every push.

### Goal

When you push code to your GitHub repository, GitHub Actions should automatically run your test command.

### Prerequisites

You need:

- A GitHub repository
- A project with a test command
- A `package.json` file if using Node.js

If you are not using Node.js, adapt the install and test commands to your language.

Examples:

```text
Node.js: npm test
Python: pytest
Go: go test ./...
Java/Maven: mvn test
```

For this exercise, the example uses Node.js.

### Step 1: Confirm your test command works locally

Run:

```bash
npm test
```

If this fails locally, fix it before adding CI.

CI should automate known project commands. It should not be the first place you discover that your project has no valid test script.

Your `package.json` should have something like:

```json
{
  "scripts": {
    "test": "echo \"replace this with real tests\" && exit 0"
  }
}
```

For a real project, this should run actual tests.

### Step 2: Create the workflow directory

From the root of your repository:

```bash
mkdir -p .github/workflows
```

### Step 3: Create the workflow file

Create:

```text
.github/workflows/test.yml
```

### Step 4: Add the workflow configuration

Paste this into `test.yml`:

```yaml
name: Run Tests

on:
  push:

jobs:
  test:
    name: Test Application
    runs-on: ubuntu-latest

    steps:
      - name: Check out repository
        uses: actions/checkout@v4

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: "20"

      - name: Install dependencies
        run: npm ci

      - name: Run tests
        run: npm test
```

### Step 5: Commit and push the workflow

Run:

```bash
git add .github/workflows/test.yml
git commit -m "Add GitHub Actions test workflow"
git push
```

### Step 6: View the workflow run

Go to your GitHub repository.

Open the **Actions** tab.

You should see a workflow named:

```text
Run Tests
```

Open the latest run and inspect the logs.

### Step 7: Read the logs like an engineer

Look for each step:

```text
Check out repository
Set up Node.js
Install dependencies
Run tests
```

For each step, ask:

- Did it start?
- Did it finish?
- How long did it take?
- If it failed, what was the first real error?

Do not only read the final red or green status. The logs explain what actually happened.

### Step 8: Intentionally break a test

Change your test script temporarily so it fails.

Example:

```json
{
  "scripts": {
    "test": "exit 1"
  }
}
```

Commit and push:

```bash
git add package.json
git commit -m "Test failing CI behavior"
git push
```

Check the Actions tab again.

You should see the workflow fail.

This is good practice because it teaches you what failure looks like.

### Step 9: Fix the test

Restore the passing test command.

Then commit and push:

```bash
git add package.json
git commit -m "Restore passing tests"
git push
```

Confirm the workflow turns green again.

### Step 10: Optional improvement — run on pull requests too

After you understand `push`, you can also run tests on pull requests:

```yaml
on:
  push:
  pull_request:
```

This means tests run when:

- Code is pushed
- A pull request is opened or updated

This is common in production teams because pull requests should be validated before merge.

## Expected Outcome

After completing the exercise, you should be able to explain and demonstrate:

- A GitHub Actions workflow that runs on every push
- How a pipeline starts from a GitHub event
- How a workflow is defined in `.github/workflows/`
- How jobs group related automation work
- How steps run commands or reusable actions
- How runners execute jobs
- How test failures stop a pipeline
- Why artifacts are used to preserve build or test outputs
- Why secrets should not be hardcoded
- How deployment gates protect production

You should also be able to describe this flow:

```text
push code
  ↓
GitHub Actions event triggers workflow
  ↓
runner starts job
  ↓
steps check out code, install dependencies, and run tests
  ↓
workflow passes or fails
```

## Quiz Questions

1. What is the difference between a workflow, a job, a step, and a runner in GitHub Actions?

2. Why should secrets not be written directly into workflow YAML files?

3. If a team wants to deploy only after tests pass and a human approves production release, what kind of CI/CD concept are they using?

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

Next, learn how CI/CD connects to container builds and deployments.

A logical next topic is:

```text
Build a container image in CI, push it to a container registry, and deploy it to a runtime environment such as Kubernetes.
```

This connects today’s CI/CD fundamentals with the previous container and Kubernetes lessons:

```text
code
  ↓
CI tests
  ↓
Docker image build
  ↓
image registry
  ↓
Kubernetes Deployment
  ↓
running Pods
```
