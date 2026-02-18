# Module 5: Docker Compose (~1 hour)

## What is Docker Compose?

Docker Compose lets you define and run **multi-container applications** with a single YAML file. Instead of running multiple `docker run` commands, you describe your entire stack declaratively.

---

## Demo 1: Simple Compose — Task API + Redis

Create `docker-compose.yml`:

```yaml
services:
  api:
    build:
      context: ../../sample-app
      dockerfile: ../day1-docker/02-images/Dockerfile.basic
    ports:
      - "5000:5000"
    environment:
      - APP_VERSION=1.0.0
      - ENVIRONMENT=development
    depends_on:
      - redis
    networks:
      - app-network

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    networks:
      - app-network

networks:
  app-network:
    driver: bridge
```

### Run it

```bash
# Start all services
docker compose up -d

# View running services
docker compose ps

# View logs
docker compose logs
docker compose logs api    # just one service

# Follow logs in real time
docker compose logs -f api

# Test the API
curl http://localhost:5000/
curl http://localhost:5000/health

# Stop everything
docker compose down
```

---

## Demo 2: Full Stack — API + Postgres + Redis

`docker-compose.full.yml`:

```yaml
services:
  api:
    build:
      context: ../../sample-app
      dockerfile: ../day1-docker/02-images/Dockerfile.basic
    ports:
      - "5000:5000"
    environment:
      - APP_VERSION=2.0.0
      - ENVIRONMENT=development
      - DB_HOST=postgres
      - REDIS_HOST=redis
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_started
    networks:
      - app-network
    restart: unless-stopped

  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: workshop
      POSTGRES_PASSWORD: workshop123
      POSTGRES_DB: tasks
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    networks:
      - app-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U workshop"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redisdata:/data
    networks:
      - app-network

volumes:
  pgdata:
  redisdata:

networks:
  app-network:
    driver: bridge
```

```bash
# Start with a specific compose file
docker compose -f docker-compose.full.yml up -d

# Check health status
docker compose -f docker-compose.full.yml ps

# Exec into postgres to verify
docker compose -f docker-compose.full.yml exec postgres psql -U workshop -d tasks -c "\dt"

# Scale a service (run 3 API instances)
# Note: remove the host port mapping for api first, or use a range
docker compose -f docker-compose.full.yml up -d --scale api=3

# Tear down (remove volumes too)
docker compose -f docker-compose.full.yml down -v
```

---

## Demo 3: Development Workflow with Hot Reload

`docker-compose.dev.yml`:

```yaml
services:
  api:
    build:
      context: ../../sample-app
      dockerfile: ../day1-docker/02-images/Dockerfile.basic
    ports:
      - "5000:5000"
    environment:
      - DEBUG=true
      - APP_VERSION=dev
    volumes:
      - ../../sample-app:/app    # Bind mount for hot reload
    command: python app.py       # Override CMD
    networks:
      - app-network

  redis:
    image: redis:7-alpine
    networks:
      - app-network

networks:
  app-network:
```

```bash
# Start in development mode
docker compose -f docker-compose.dev.yml up -d

# Edit sample-app/app.py on your host — changes are reflected!
# (Python needs a restart; use a watcher for true hot reload)

# Rebuild after dependency changes
docker compose -f docker-compose.dev.yml up -d --build

# Clean up
docker compose -f docker-compose.dev.yml down
```

---

## Demo 4: Environment Variables and .env Files

Create `.env`:

```
APP_VERSION=3.0.0
POSTGRES_PASSWORD=supersecret
ENVIRONMENT=staging
```

`docker-compose.env.yml`:

```yaml
services:
  api:
    build:
      context: ../../sample-app
      dockerfile: ../day1-docker/02-images/Dockerfile.basic
    ports:
      - "5000:5000"
    environment:
      - APP_VERSION=${APP_VERSION}
      - ENVIRONMENT=${ENVIRONMENT}

  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: tasks
```

```bash
# Variables from .env are substituted automatically
docker compose -f docker-compose.env.yml config  # Preview resolved config

docker compose -f docker-compose.env.yml up -d
curl http://localhost:5000/env  # Shows the substituted values
docker compose -f docker-compose.env.yml down
```

---

## Essential Compose Commands

```bash
docker compose up -d                 # Start services in background
docker compose down                  # Stop and remove containers
docker compose down -v               # Also remove volumes
docker compose ps                    # List running services
docker compose logs [-f] [SERVICE]   # View logs
docker compose exec SERVICE CMD      # Run command in service
docker compose build                 # Rebuild images
docker compose up -d --build         # Rebuild and restart
docker compose config                # Validate and view resolved config
docker compose pull                  # Pull latest images
docker compose restart [SERVICE]     # Restart services
```

---

## Exercises for Participants

1. Write a compose file that runs WordPress + MySQL with persistent volumes
2. Add a healthcheck to ensure the API only starts after the database is ready
3. Use an `.env` file to externalize all passwords and config
4. Set up a development compose file with bind mounts for your own project
