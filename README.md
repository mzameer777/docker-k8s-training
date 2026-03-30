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

## Take-Home Assignments

Practice after each day with hands-on assignments that build a complete, production-grade application from scratch:

| Assignment File | Contents |
| --------------- | -------- |
| [assignments/day1-docker-assignments.md](assignments/day1-docker-assignments.md) | 5 assignments + a bonus CI challenge covering Dockerfiles, multi-stage builds, volumes, Compose, and security hardening |
| [assignments/day2-kubernetes-assignments.md](assignments/day2-kubernetes-assignments.md) | 5 assignments + a capstone project covering Deployments, rolling updates, full stack K8s, RBAC, and HPA |
| [assignments/cheatsheet.md](assignments/cheatsheet.md) | Full Docker + Kubernetes command reference |

Each day's assignments build on each other, culminating in a **Capstone Assignment** where participants deploy a secure, auto-scaling, fully configured application stack on Kubernetes.

