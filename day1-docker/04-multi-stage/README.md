# Module 4: Multi-Stage Builds (~45 min)

## Why Multi-Stage Builds?

Single-stage builds include build tools, compilers, and dev dependencies in the final image. Multi-stage builds let you **use one stage to build** and **copy only the result** into a slim final image.

```
Single-Stage:  Build tools + Source + App binary  →  LARGE image (500MB+)
Multi-Stage:   Stage 1 (build) → Stage 2 (copy binary only) → SMALL image (50MB)
```

---

## Demo 1: Single-Stage vs Multi-Stage (Go Example)

### The Go application

Create `hello.go`:

```go
package main

import (
    "fmt"
    "net/http"
)

func main() {
    http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
        fmt.Fprintf(w, "Hello from Go! Multi-stage builds are awesome!")
    })
    fmt.Println("Server starting on :8080")
    http.ListenAndServe(":8080", nil)
}
```

### Single-stage (BAD)

`Dockerfile.single`:

```dockerfile
FROM golang:1.22
WORKDIR /app
COPY hello.go .
RUN go build -o hello hello.go
CMD ["./hello"]
```

### Multi-stage (GOOD)

`Dockerfile.multi`:

```dockerfile
# Stage 1: Build
FROM golang:1.22 AS builder
WORKDIR /app
COPY hello.go .
RUN CGO_ENABLED=0 go build -o hello hello.go

# Stage 2: Run (minimal image)
FROM alpine:3.19
WORKDIR /app
COPY --from=builder /app/hello .
CMD ["./hello"]
```

### Compare

```bash
docker build -f Dockerfile.single -t hello-single .
docker build -f Dockerfile.multi -t hello-multi .

docker images | grep hello
# hello-single  ~800MB
# hello-multi   ~15MB  ← 50x smaller!

# Both work the same
docker run --rm -p 8080:8080 hello-multi
curl http://localhost:8080
```

---

## Demo 2: Multi-Stage Python App

`Dockerfile.python-multi`:

```dockerfile
# Stage 1: Install dependencies in a virtual env
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Copy venv + app into clean image
FROM python:3.12-slim
WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY app.py .

EXPOSE 5000
CMD ["python", "app.py"]
```

```bash
cd sample-app/
docker build -f ../day1-docker/04-multi-stage/Dockerfile.python-multi -t task-api:multi .
docker images | grep task-api
```

---

## Demo 3: Multi-Stage with Testing

`Dockerfile.with-tests`:

```dockerfile
# Stage 1: Install dependencies
FROM python:3.12-slim AS base
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Run tests
FROM base AS test
COPY . .
RUN pip install pytest
RUN pytest tests/ -v

# Stage 3: Production image (only built if tests pass)
FROM base AS production
COPY app.py .
EXPOSE 5000
CMD ["python", "app.py"]
```

```bash
# Build the production target — tests run automatically in an intermediate stage
docker build -f Dockerfile.with-tests --target production -t task-api:tested .

# If tests fail, the build fails!
```

---

## Demo 4: Using --target to Build Specific Stages

```bash
# Build only up to the test stage
docker build -f Dockerfile.with-tests --target test -t task-api:test-only .

# Build only the production stage
docker build -f Dockerfile.with-tests --target production -t task-api:prod .
```

---

## Demo 5: Scratch Image (Ultra-Minimal)

For statically compiled binaries, you can use the `scratch` image (literally empty):

```dockerfile
FROM golang:1.22 AS builder
WORKDIR /app
COPY hello.go .
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w" -o hello hello.go

FROM scratch
COPY --from=builder /app/hello /hello
CMD ["/hello"]
```

```bash
docker build -f Dockerfile.scratch -t hello-scratch .
docker images | grep hello-scratch
# ~5MB — just the binary, nothing else!
```

---

## Key Takeaways

1. Multi-stage builds keep production images **small and secure**
2. Build tools never ship in the final image
3. Use `--target` to build specific stages
4. `COPY --from=stagename` copies artifacts between stages
5. Great for CI/CD: test stage gates the production stage

---

## Exercises for Participants

1. Convert the sample Task API to use a multi-stage build
2. Add a test stage that runs before the production stage
3. Try building a Go app with `scratch` as the final base
4. Compare image sizes between single-stage, multi-stage, and scratch builds
