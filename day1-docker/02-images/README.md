# Module 2: Building Docker Images (~1.5 hours)

## Dockerfile Basics

A Dockerfile is a recipe for building an image. Each instruction creates a **layer**.

### Dockerfile Instructions Reference

| Instruction  | Purpose                                      | Example                              |
| ------------ | -------------------------------------------- | ------------------------------------ |
| `FROM`       | Base image                                   | `FROM python:3.12-slim`              |
| `WORKDIR`    | Set working directory                        | `WORKDIR /app`                       |
| `COPY`       | Copy files from host to image                | `COPY . .`                           |
| `ADD`        | Like COPY but can extract archives / fetch URLs | `ADD app.tar.gz /app`             |
| `RUN`        | Execute command during build                 | `RUN pip install -r requirements.txt`|
| `CMD`        | Default command when container starts        | `CMD ["python", "app.py"]`           |
| `ENTRYPOINT` | Fixed command (CMD becomes arguments)        | `ENTRYPOINT ["python"]`              |
| `EXPOSE`     | Document which port the app uses             | `EXPOSE 5000`                        |
| `ENV`        | Set environment variable                     | `ENV APP_ENV=production`             |
| `ARG`        | Build-time variable                          | `ARG VERSION=1.0`                    |
| `LABEL`      | Add metadata                                 | `LABEL maintainer="you@example.com"` |

---

## Demo 1: Build Your First Image

We'll containerize the sample Task API app.

### Step 1 — Create a simple Dockerfile

```bash
cd sample-app/
```

Create `Dockerfile.basic`:

```dockerfile
# Start from a Python base image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Copy dependency file first (for better caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .

# Document the port
EXPOSE 5000

# Set environment variable
ENV APP_VERSION=1.0.0

# Command to run when container starts
CMD ["python", "app.py"]
```

### Step 2 — Build and run

```bash
# Build the image (-t = tag/name)
docker build -f Dockerfile.basic -t task-api:1.0 .

# Run the container
docker run -d --name task-api -p 5000:5000 task-api:1.0

# Test it
curl http://localhost:5000/
curl http://localhost:5000/health
curl -X POST http://localhost:5000/tasks -H "Content-Type: application/json" -d '{"title":"Learn Docker"}'
curl http://localhost:5000/tasks

# Clean up
docker stop task-api && docker rm task-api
```

---

## Demo 2: Understanding Layers and Caching

```bash
# Build the image and observe the layers
docker build -f Dockerfile.basic -t task-api:1.0 .

# Notice: "Using cache" for unchanged layers

# Now modify app.py (add a comment at the top)
# Rebuild — only layers AFTER the change are rebuilt
docker build -f Dockerfile.basic -t task-api:1.1 .

# View image layers
docker history task-api:1.0
```

### Why order matters

```
BAD ORDER (cache busts on every code change):
  COPY . .                    ← changes every time you edit code
  RUN pip install ...         ← re-runs even though requirements didn't change

GOOD ORDER (dependencies cached separately):
  COPY requirements.txt .    ← only changes when deps change
  RUN pip install ...         ← cached if requirements.txt unchanged
  COPY . .                    ← only this layer rebuilds on code change
```

---

## Demo 3: ENTRYPOINT vs CMD

```bash
# CMD — easily overridden
docker run task-api:1.0 echo "I replaced the CMD"

# ENTRYPOINT — fixed command, CMD becomes arguments
```

Create `Dockerfile.entrypoint`:

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
ENTRYPOINT ["python"]
CMD ["app.py"]
```

```bash
docker build -f Dockerfile.entrypoint -t task-api:entrypoint .

# Default: runs "python app.py"
docker run --rm task-api:entrypoint

# Override CMD: runs "python --version"
docker run --rm task-api:entrypoint --version

# Override ENTRYPOINT: runs bash
docker run --rm --entrypoint bash task-api:entrypoint -c "echo hello"
```

---

## Demo 4: Build Arguments (ARG)

Create `Dockerfile.arg`:

```dockerfile
FROM python:3.12-slim

ARG APP_VERSION=1.0.0
ARG BUILD_DATE

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .

ENV APP_VERSION=${APP_VERSION}

LABEL build_date=${BUILD_DATE}
LABEL version=${APP_VERSION}

CMD ["python", "app.py"]
```

```bash
# Build with custom arguments
docker build -f Dockerfile.arg \
  --build-arg APP_VERSION=2.0.0 \
  --build-arg BUILD_DATE=$(date -u +%Y-%m-%dT%H:%M:%SZ) \
  -t task-api:2.0 .

# Verify
docker run --rm task-api:2.0 python -c "import os; print(os.getenv('APP_VERSION'))"
docker inspect task-api:2.0 | grep -A2 "Labels"
```

---

## Demo 5: .dockerignore

Create `.dockerignore` in the sample-app directory:

```
__pycache__
*.pyc
.git
.env
*.md
tests/
.venv
node_modules
```

```bash
# Show the build context size difference
# Without .dockerignore — all files sent to Docker daemon
# With .dockerignore — excluded files are skipped

docker build -f Dockerfile.basic -t task-api:ignore-test .
```

---

## Demo 6: Tagging and Pushing

```bash
# Tag an existing image with a new name
docker tag task-api:1.0 myregistry/task-api:1.0
docker tag task-api:1.0 myregistry/task-api:latest

# List to see all tags
docker images | grep task-api

# Push to a registry (requires docker login)
# docker login
# docker push myregistry/task-api:1.0
# docker push myregistry/task-api:latest
```

---

## Exercises for Participants

1. Write a Dockerfile for a Node.js app (use `node:20-alpine`, `npm install`, `npm start`)
2. Build the Task API with a custom `APP_VERSION` using build args
3. Create a `.dockerignore` file and verify the build context is smaller
4. Experiment with layer ordering — put `COPY . .` before `RUN pip install` and observe what happens to caching

---

## Quick Reference

```bash
docker build -t NAME:TAG .              # Build image from Dockerfile
docker build -f FILE -t NAME:TAG .      # Build from specific Dockerfile
docker build --build-arg KEY=VAL .      # Pass build arguments
docker tag SOURCE TARGET                # Create a new tag for an image
docker push IMAGE:TAG                   # Push to registry
docker history IMAGE                    # Show image layers
```
