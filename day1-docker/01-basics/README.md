# Module 1: Docker Basics (~1.5 hours)

## What is Docker?

Docker is a platform that packages applications and their dependencies into lightweight, portable **containers**. Unlike virtual machines, containers share the host OS kernel, making them fast and efficient.

```
┌─────────────────────────────────┐     ┌─────────────────────────────────┐
│         Virtual Machines        │     │          Containers             │
├─────────────────────────────────┤     ├─────────────────────────────────┤
│  ┌───────┐ ┌───────┐ ┌───────┐  │     │  ┌───────┐ ┌───────┐ ┌───────┐  │
│  │ App A │ │ App B │ │ App C │  │     │  │ App A │ │ App B │ │ App C │  │
│  ├───────┤ ├───────┤ ├───────┤  │     │  ├───────┤ ├───────┤ ├───────┤  │
│  │ Libs  │ │ Libs  │ │ Libs  │  │     │  │ Libs  │ │ Libs  │ │ Libs  │  │
│  ├───────┤ ├───────┤ ├───────┤  │     │  └───────┘ └───────┘ └───────┘  │
│  │Guest  │ │Guest  │ │Guest  │  │     ├─────────────────────────────────┤
│  │  OS   │ │  OS   │ │  OS   │  │     │        Docker Engine            │
│  └───────┘ └───────┘ └───────┘  │     ├─────────────────────────────────┤
├─────────────────────────────────┤     │          Host OS                │
│         Hypervisor              │     ├─────────────────────────────────┤
├─────────────────────────────────┤     │        Infrastructure           │
│          Host OS                │     └─────────────────────────────────┘
├─────────────────────────────────┤
│        Infrastructure           │
└─────────────────────────────────┘
```

## Key Concepts

| Concept    | Description                                              |
| ---------- | -------------------------------------------------------- |
| **Image**  | A read-only template with instructions for creating a container |
| **Container** | A running instance of an image                        |
| **Registry** | A storage and distribution system for images (e.g., Docker Hub) |
| **Dockerfile** | A text file with instructions to build an image      |

---

## Demo 1: Your First Container

### Run a simple container

```bash
# Pull and run an nginx container
docker run -d --name my-first-container -p 8080:80 nginx

# Visit http://localhost:8080 in your browser
```

### Verify it's running

```bash
# List running containers
docker ps

# View container logs
docker logs my-first-container

# Inspect the container
docker inspect my-first-container
```

### Interact with the container

```bash
# Execute a command inside the running container
docker exec -it my-first-container bash

# Inside the container, run:
cat /etc/os-release
ls /usr/share/nginx/html/
exit
```

### Stop and remove

```bash
docker stop my-first-container
docker rm my-first-container
```

---

## Demo 2: Container Lifecycle

```bash
# Create a container (but don't start it)
docker create --name lifecycle-demo alpine echo "Hello from container!"

# List all containers (including stopped)
docker ps -a

# Start the container
docker start lifecycle-demo

# Check logs to see the output
docker logs lifecycle-demo

# Restart the container
docker restart lifecycle-demo

# Pause and unpause
docker run -d --name pause-demo nginx
docker pause pause-demo
docker ps  # Notice the "Paused" status
docker unpause pause-demo

# Clean up
docker stop pause-demo
docker rm lifecycle-demo pause-demo
```

---

## Demo 3: Exploring Images

```bash
# List local images
docker images

# Pull specific image versions (tags)
docker pull python:3.12-slim
docker pull python:3.12-alpine
docker pull python:3.12

# Compare image sizes
docker images | grep python

# Inspect image layers
docker history python:3.12-slim

# Remove an image
docker rmi python:3.12
```

---

## Demo 4: Environment Variables and Port Mapping

```bash
# Run MySQL with environment variables
docker run -d \
  --name demo-mysql \
  -e MYSQL_ROOT_PASSWORD=workshop123 \
  -e MYSQL_DATABASE=workshop \
  -p 3306:3306 \
  mysql:8

# Verify the database was created
docker exec -it demo-mysql mysql -uroot -pworkshop123 -e "SHOW DATABASES;"

# Clean up
docker stop demo-mysql && docker rm demo-mysql
```

---

## Demo 5: Resource Limits

```bash
# Run a container with memory and CPU limits
docker run -d \
  --name limited-container \
  --memory=256m \
  --cpus=0.5 \
  nginx

# Check resource usage
docker stats limited-container --no-stream

# Clean up
docker stop limited-container && docker rm limited-container
```

---

## Exercises for Participants

1. Run a `redis` container on port 6379 and connect to it using `docker exec`
2. Run a `postgres:16` container with a custom database name and password
3. Pull 3 different tags of the `node` image and compare their sizes
4. Run two nginx containers on different ports (8081 and 8082)

---

## Quick Reference

```bash
docker run [OPTIONS] IMAGE [COMMAND]    # Create and start a container
docker ps                                # List running containers
docker ps -a                             # List all containers
docker stop CONTAINER                    # Stop a container
docker rm CONTAINER                      # Remove a container
docker images                            # List images
docker pull IMAGE:TAG                    # Download an image
docker exec -it CONTAINER COMMAND        # Run command in container
docker logs CONTAINER                    # View container logs
docker inspect CONTAINER                 # Detailed container info
docker stats                             # Live resource usage
```
