# Day 1 Take-Home Assignments: Docker

These are short, focused exercises — each one should take 10–20 minutes. The goal is to get comfortable with the core Docker concepts covered today.

---

## Assignment 1: Run and Explore Containers

**Concept:** Container lifecycle, running containers, viewing logs.

1. Pull and run an `nginx` container on port `8888`:
   ```bash
   docker run -d --name my-nginx -p 8888:80 nginx
   ```
2. Open `http://localhost:8888` in your browser — you should see the nginx welcome page.
3. View the logs:
   ```bash
   docker logs my-nginx
   ```
4. Get a shell inside the container and look around:
   ```bash
   docker exec -it my-nginx bash
   ls /usr/share/nginx/html/
   exit
   ```
5. Stop and remove the container:
   ```bash
   docker stop my-nginx
   docker rm my-nginx
   ```

**Questions to think about:**
- What happened when you stopped the container?
- Where does nginx serve files from inside the container?

---

## Assignment 2: Build Your First Image

**Concept:** Writing a Dockerfile, building an image, running it.

1. Create a new folder called `my-app` and inside it create two files:

   `app.py`:
   ```python
   print("Hello from my Docker container!")
   print("Docker is pretty cool.")
   ```

   `Dockerfile`:
   ```dockerfile
   FROM python:3.12-slim
   WORKDIR /app
   COPY app.py .
   CMD ["python", "app.py"]
   ```

2. Build the image:
   ```bash
   docker build -t my-app:1.0 .
   ```

3. Run it:
   ```bash
   docker run --rm my-app:1.0
   ```
   You should see both print statements in the output.

4. Now edit `app.py` to print your name, rebuild with tag `my-app:2.0`, and run it. Notice how fast the rebuild is (cached layers).

**Questions to think about:**
- What does `WORKDIR` do?
- What does `--rm` do when running a container?

---

## Assignment 3: Keep Data with Volumes

**Concept:** Why data is lost without volumes, and how to fix it.

**Part A — See the problem:**
```bash
# Start a container and create a file inside it
docker run -it --name test-data alpine sh -c "echo 'my important note' > /note.txt && cat /note.txt"

# Remove the container
docker rm test-data

# Start a new container — the file is gone!
docker run --rm alpine cat /note.txt
```

**Part B — Fix it with a volume:**
```bash
# Run with a named volume
docker run --name with-volume -v my-notes:/data alpine sh -c "echo 'my important note' > /data/note.txt"

# Remove the container
docker rm with-volume

# New container, same volume — data is still there!
docker run --rm -v my-notes:/data alpine cat /data/note.txt

# Clean up
docker volume rm my-notes
```

**Questions to think about:**
- When would you use a volume in a real application?
- What kinds of data should be stored in volumes? (Think: databases, uploads, logs)

---

## Assignment 4: Docker Compose — Two Containers Talking

**Concept:** Running multiple containers together, service discovery by name.

1. Create a folder called `compose-demo` with a `docker-compose.yml`:

   ```yaml
   services:
     web:
       image: nginx
       ports:
         - "8080:80"
       networks:
         - demo-net

     redis:
       image: redis:alpine
       networks:
         - demo-net

   networks:
     demo-net:
   ```

2. Start both services:
   ```bash
   docker compose up -d
   ```

3. Check they're running:
   ```bash
   docker compose ps
   ```

4. Prove the `web` container can reach `redis` by name:
   ```bash
   docker compose exec web sh -c "apt-get update -q && apt-get install -q -y iputils-ping && ping -c 3 redis"
   ```

5. Tear it all down:
   ```bash
   docker compose down
   ```

**Questions to think about:**
- How did the `web` container know where `redis` was? (No IPs needed!)
- What does `docker compose down` do vs just stopping the containers?

---

## Bonus: Image Size Comparison

This one is just a quick observation — no coding needed.

```bash
# Pull a few different Python image variants
docker pull python:3.12
docker pull python:3.12-slim
docker pull python:3.12-alpine

# Compare the sizes
docker images | grep python
```

Look at the SIZE column. Write down the sizes and think:
- Why would you choose `slim` or `alpine` over the full image in production?
- What might you lose by using the smaller images?

---

## Checklist

Before Day 2, make sure you can answer these:

```
[ ] How do you run a container in the background?
[ ] How do you see the logs of a running container?
[ ] What is a Dockerfile and what does it produce?
[ ] Why does data disappear when a container is removed?
[ ] What problem does a volume solve?
[ ] How do containers in the same Compose network find each other?
```
