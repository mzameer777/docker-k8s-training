# Module 3: Volumes & Networks (~1 hour)

## Docker Volumes

Containers are **ephemeral** — when removed, their data is gone. Volumes solve this.

### Types of Storage

| Type           | Description                          | Use Case                    |
| -------------- | ------------------------------------ | --------------------------- |
| **Volume**     | Managed by Docker, stored on host    | Databases, persistent data  |
| **Bind Mount** | Maps a host path into the container  | Development, config files   |
| **tmpfs**      | In-memory only, never written to disk| Secrets, temp data          |

---

## Demo 1: Data Loss Without Volumes

```bash
# Run a container, create a file, then remove the container
docker run -it --name no-volume alpine sh -c "echo 'important data' > /data.txt && cat /data.txt"

# Container exited — start and check
docker start -i no-volume
# cat /data.txt  --> data still there (container exists)

# Remove the container entirely
docker rm no-volume

# Run a new container — data is gone!
docker run --rm alpine cat /data.txt  # ERROR: file not found
```

---

## Demo 2: Named Volumes

```bash
# Create a named volume
docker volume create workshop-data

# Run a container with the volume mounted
docker run -d --name writer \
  -v workshop-data:/app/data \
  alpine sh -c "while true; do date >> /app/data/log.txt; sleep 2; done"

# Read from the same volume in another container
docker run --rm -v workshop-data:/data alpine cat /data/log.txt

# Stop the writer
docker stop writer && docker rm writer

# Data persists! Run another container to verify
docker run --rm -v workshop-data:/data alpine cat /data/log.txt

# Inspect the volume
docker volume inspect workshop-data

# Clean up
docker volume rm workshop-data
```

---

## Demo 3: Bind Mounts (Development Workflow)

```bash
# Mount current directory into the container
# Great for development — edit locally, changes reflected immediately

cd sample-app/

docker run -d --name dev-api \
  -v $(pwd):/app \
  -w /app \
  -p 5000:5000 \
  python:3.12-slim \
  sh -c "pip install flask && python app.py"

# Test it
curl http://localhost:5000/

# Now edit app.py on your host machine
# The container sees changes immediately (restart may be needed for Python)

# Clean up
docker stop dev-api && docker rm dev-api
```

---

## Demo 4: Postgres with Persistent Storage

```bash
# Run Postgres with a volume for data persistence
docker run -d --name demo-postgres \
  -e POSTGRES_PASSWORD=workshop123 \
  -e POSTGRES_DB=workshop \
  -v pgdata:/var/lib/postgresql/data \
  -p 5432:5432 \
  postgres:16

# Create a table and insert data
docker exec -it demo-postgres psql -U postgres -d workshop -c "
  CREATE TABLE students (id SERIAL PRIMARY KEY, name TEXT);
  INSERT INTO students (name) VALUES ('Alice'), ('Bob');
  SELECT * FROM students;
"

# Stop and remove the container
docker stop demo-postgres && docker rm demo-postgres

# Start a NEW container with the same volume — data persists!
docker run -d --name demo-postgres-2 \
  -e POSTGRES_PASSWORD=workshop123 \
  -v pgdata:/var/lib/postgresql/data \
  -p 5432:5432 \
  postgres:16

# Verify data survived
sleep 3  # wait for postgres to start
docker exec -it demo-postgres-2 psql -U postgres -d workshop -c "SELECT * FROM students;"

# Clean up
docker stop demo-postgres-2 && docker rm demo-postgres-2
docker volume rm pgdata
```

---

## Docker Networks

By default, containers are isolated. Networks let containers communicate with each other.

### Network Types

| Driver     | Description                                    |
| ---------- | ---------------------------------------------- |
| `bridge`   | Default. Containers on same bridge can talk     |
| `host`     | Container shares host's network stack           |
| `none`     | No networking                                  |
| `overlay`  | Multi-host networking (Docker Swarm)            |

---

## Demo 5: Default Bridge Network

```bash
# Run two containers on the default bridge
docker run -d --name container-a alpine sleep 3600
docker run -d --name container-b alpine sleep 3600

# They CANNOT reach each other by name on the default bridge
docker exec container-a ping -c 2 container-b  # FAILS

# But they CAN reach each other by IP
CONTAINER_B_IP=$(docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' container-b)
docker exec container-a ping -c 2 $CONTAINER_B_IP  # WORKS

# Clean up
docker stop container-a container-b && docker rm container-a container-b
```

---

## Demo 6: Custom Bridge Network (DNS Discovery)

```bash
# Create a custom network
docker network create workshop-net

# Run containers on the custom network
docker run -d --name app --network workshop-net alpine sleep 3600
docker run -d --name db --network workshop-net alpine sleep 3600

# Now they CAN reach each other BY NAME (automatic DNS)
docker exec app ping -c 2 db       # WORKS!
docker exec db ping -c 2 app       # WORKS!

# Inspect the network
docker network inspect workshop-net

# Clean up
docker stop app db && docker rm app db
docker network rm workshop-net
```

---

## Demo 7: Network Isolation

```bash
# Create two separate networks
docker network create frontend
docker network create backend

# Frontend container — on frontend network only
docker run -d --name web --network frontend alpine sleep 3600

# Backend container — on backend network only
docker run -d --name api --network backend alpine sleep 3600

# Shared container — on BOTH networks
docker run -d --name gateway --network frontend alpine sleep 3600
docker network connect backend gateway

# web can reach gateway, but NOT api
docker exec web ping -c 2 gateway   # WORKS
docker exec web ping -c 2 api       # FAILS

# gateway can reach both
docker exec gateway ping -c 2 web   # WORKS
docker exec gateway ping -c 2 api   # WORKS

# Clean up
docker stop web api gateway && docker rm web api gateway
docker network rm frontend backend
```

---

## Exercises for Participants

1. Create a named volume, run a container that writes a file to it, remove the container, and verify the data persists in a new container
2. Set up a bind mount to serve a custom `index.html` via nginx
3. Create a custom network and run Redis + the Task API on it so the API can reach Redis by name
4. Demonstrate network isolation: create two networks and prove containers on separate networks cannot communicate

---

## Quick Reference

```bash
# Volumes
docker volume create NAME               # Create a volume
docker volume ls                         # List volumes
docker volume inspect NAME               # Volume details
docker volume rm NAME                    # Delete a volume
docker run -v NAME:/path IMAGE           # Mount named volume
docker run -v /host/path:/path IMAGE     # Bind mount

# Networks
docker network create NAME              # Create a network
docker network ls                        # List networks
docker network inspect NAME              # Network details
docker network connect NET CONTAINER     # Add container to network
docker network disconnect NET CONTAINER  # Remove container from network
docker network rm NAME                   # Delete a network
```
