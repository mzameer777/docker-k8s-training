# Docker & Kubernetes Workshop (2 Days)

A hands-on workshop covering Docker fundamentals through advanced Kubernetes concepts. Each module includes explanations, live demos, and exercises.

## Prerequisites

- **Docker Desktop** installed ([download](https://www.docker.com/products/docker-desktop/))
- **kubectl** installed (`brew install kubectl` or [install guide](https://kubernetes.io/docs/tasks/tools/))
- **A local Kubernetes cluster** (one of):
  - Docker Desktop (enable Kubernetes in settings)
  - minikube (`brew install minikube && minikube start`)
  - kind (`brew install kind && kind create cluster`)
- **Helm** (for Day 2 advanced): `brew install helm`
- A terminal and text editor

## Workshop Structure

### Day 1: Docker (6 hours)

| Time          | Module | Topic                                         |
| ------------- | ------ | --------------------------------------------- |
| 09:00 - 10:30 | [01](day1-docker/01-basics/)         | **Docker Basics** — containers, images, lifecycle |
| 10:30 - 10:45 |        | *Break*                                       |
| 10:45 - 12:15 | [02](day1-docker/02-images/)         | **Building Images** — Dockerfiles, layers, caching |
| 12:15 - 13:15 |        | *Lunch*                                       |
| 13:15 - 14:15 | [03](day1-docker/03-volumes-networks/) | **Volumes & Networks** — persistence, DNS, isolation |
| 14:15 - 15:00 | [04](day1-docker/04-multi-stage/)    | **Multi-Stage Builds** — optimized images     |
| 15:00 - 15:15 |        | *Break*                                       |
| 15:15 - 16:15 | [05](day1-docker/05-compose/)        | **Docker Compose** — multi-container apps     |
| 16:15 - 16:45 | [06](day1-docker/06-best-practices/) | **Best Practices & Security**                 |
| 16:45 - 17:00 |        | *Day 1 Wrap-up & Q&A*                         |

### Day 2: Kubernetes (6 hours)

| Time          | Module | Topic                                         |
| ------------- | ------ | --------------------------------------------- |
| 09:00 - 10:00 | [01](day2-kubernetes/01-basics/)     | **K8s Basics** — architecture, kubectl, pods  |
| 10:00 - 10:15 |        | *Break*                                       |
| 10:15 - 11:45 | [02](day2-kubernetes/02-pods-deployments/) | **Deployments** — scaling, rolling updates, rollbacks |
| 11:45 - 12:45 |        | *Lunch*                                       |
| 12:45 - 13:45 | [03](day2-kubernetes/03-services-networking/) | **Services & Networking** — ClusterIP, NodePort, Ingress |
| 13:45 - 14:30 | [04](day2-kubernetes/04-configmaps-secrets/) | **ConfigMaps & Secrets** — externalized config |
| 14:30 - 14:45 |        | *Break*                                       |
| 14:45 - 15:30 | [05](day2-kubernetes/05-storage/)    | **Persistent Storage** — PVC, StatefulSets    |
| 15:30 - 17:00 | [06](day2-kubernetes/06-advanced/)   | **Advanced** — HPA, Jobs, RBAC, Network Policies, Helm |

## Repository Layout

```
docker-k8s-training/
├── README.md                          ← You are here
├── sample-app/                        ← Demo Flask API used throughout
│   ├── app.py
│   ├── requirements.txt
│   ├── tests/
│   └── .dockerignore
├── day1-docker/
│   ├── 01-basics/                     ← Container lifecycle, images, env vars
│   ├── 02-images/                     ← Dockerfiles, layers, caching, tags
│   ├── 03-volumes-networks/           ← Volumes, bind mounts, networks, DNS
│   ├── 04-multi-stage/                ← Multi-stage builds, scratch images
│   ├── 05-compose/                    ← Docker Compose, multi-service apps
│   └── 06-best-practices/            ← Security, production Dockerfiles
└── day2-kubernetes/
    ├── 01-basics/                     ← Architecture, kubectl, pods, namespaces
    ├── 02-pods-deployments/           ← Deployments, scaling, rollbacks, probes
    ├── 03-services-networking/        ← Service types, DNS, Ingress
    ├── 04-configmaps-secrets/         ← Configuration management
    ├── 05-storage/                    ← PVC, StatefulSets, emptyDir
    └── 06-advanced/                   ← HPA, Jobs, RBAC, NetworkPolicies, Helm
```

## Sample Application

A simple **Task API** built with Flask, used for demos throughout both days:

```bash
# Endpoints
GET  /            → Service info (hostname, version)
GET  /health      → Health check
GET  /ready       → Readiness check
GET  /tasks       → List tasks
POST /tasks       → Create task (JSON: {"title": "..."})
PUT  /tasks/:id   → Update task
DELETE /tasks/:id  → Delete task
GET  /env         → Show environment variables
```

## How to Use This Workshop

1. **Follow along**: Each module's README has step-by-step instructions
2. **Run the demos**: Copy-paste commands into your terminal
3. **Do the exercises**: Each module ends with hands-on exercises
4. **Clean up**: Each demo includes cleanup commands to reset your environment

## Tips for Presenters

- Run demos live — mistakes are learning opportunities
- Let participants try exercises before showing solutions
- Use `kubectl get pods -w` and `docker compose logs -f` to show real-time behavior
- Keep a "parking lot" for questions that go beyond the current module
