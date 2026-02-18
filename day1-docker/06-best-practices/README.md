# Module 6: Docker Best Practices & Security (~30 min)

## Image Best Practices

### 1. Use Specific Tags (Never `latest` in Production)

```dockerfile
# BAD
FROM python:latest

# GOOD
FROM python:3.12-slim
```

### 2. Use Slim/Alpine Base Images

```bash
# Compare sizes
docker pull python:3.12          # ~1GB
docker pull python:3.12-slim     # ~150MB
docker pull python:3.12-alpine   # ~50MB
```

### 3. Minimize Layers — Combine RUN Commands

```dockerfile
# BAD — 3 layers
RUN apt-get update
RUN apt-get install -y curl
RUN rm -rf /var/lib/apt/lists/*

# GOOD — 1 layer, also cleans up
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*
```

### 4. Order Instructions for Cache Efficiency

```dockerfile
# Dependencies change rarely — cached
COPY requirements.txt .
RUN pip install -r requirements.txt

# Code changes often — only this rebuilds
COPY . .
```

### 5. Use .dockerignore

```
.git
.env
__pycache__
node_modules
*.md
tests/
.venv
```

---

## Security Best Practices

### 1. Don't Run as Root

```dockerfile
# Create a non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Switch to that user
USER appuser

CMD ["python", "app.py"]
```

### Demo: Root vs Non-Root

```bash
# Default: runs as root
docker run --rm alpine whoami
# Output: root

# With USER directive
docker run --rm --user 1000:1000 alpine whoami
# Output: whoami: unknown uid 1000 (but it's running as UID 1000)
```

### 2. Scan Images for Vulnerabilities

```bash
# Docker Scout (built-in)
docker scout cves task-api:1.0

# Or use Trivy
# docker run --rm aquasec/trivy image task-api:1.0
```

### 3. Don't Store Secrets in Images

```dockerfile
# BAD — secret baked into image
ENV API_KEY=supersecret123

# GOOD — pass at runtime
# docker run -e API_KEY=supersecret123 myapp
```

### 4. Use Read-Only Filesystem

```bash
docker run --rm --read-only \
  --tmpfs /tmp \
  alpine sh -c "echo 'test' > /tmp/ok.txt && echo 'tmp works' && echo 'test' > /fail.txt"
# Writing to /tmp works, writing to / fails
```

### 5. Drop Capabilities

```bash
# Drop all capabilities, add only what's needed
docker run --rm \
  --cap-drop ALL \
  --cap-add NET_BIND_SERVICE \
  nginx
```

---

## Production Checklist

```
[ ] Use specific base image tags
[ ] Use multi-stage builds
[ ] Run as non-root user
[ ] Scan for vulnerabilities
[ ] Use .dockerignore
[ ] No secrets in Dockerfile or image
[ ] Set resource limits (memory, CPU)
[ ] Use health checks
[ ] Pin dependency versions
[ ] Use read-only filesystem where possible
```

---

## Demo: Putting It All Together — Production Dockerfile

`Dockerfile.production`:

```dockerfile
# Stage 1: Build
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Production
FROM python:3.12-slim

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application
COPY app.py .

# Switch to non-root user
USER appuser

# Metadata
LABEL maintainer="workshop@example.com"
LABEL version="1.0.0"

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')"

CMD ["python", "app.py"]
```

```bash
cd sample-app/
docker build -f ../day1-docker/06-best-practices/Dockerfile.production -t task-api:production .
docker run -d --name prod-api \
  --memory=256m \
  --cpus=0.5 \
  --read-only \
  --tmpfs /tmp \
  -p 5000:5000 \
  task-api:production

# Verify health check
docker inspect --format='{{.State.Health.Status}}' prod-api

# Clean up
docker stop prod-api && docker rm prod-api
```
