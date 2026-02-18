# Module 1: Kubernetes Basics (~1 hour)

## What is Kubernetes?

Kubernetes (K8s) is a container **orchestration** platform. It automates deployment, scaling, and management of containerized applications.

### Why Kubernetes?

| Challenge                  | Docker Alone          | Kubernetes                           |
| -------------------------- | --------------------- | ------------------------------------ |
| Run on multiple machines   | Manual setup          | Automatic scheduling                 |
| Self-healing               | `--restart` flag      | Detects failures, replaces pods      |
| Scaling                    | Manual `docker run`   | `kubectl scale` or auto-scaling      |
| Load balancing             | External setup        | Built-in Services                    |
| Rolling updates            | Manual process        | Zero-downtime deployments            |
| Configuration management   | Env vars / files      | ConfigMaps & Secrets                 |

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     CONTROL PLANE                           │
│  ┌──────────┐  ┌───────────┐  ┌──────────┐  ┌───────────┐  │
│  │ API      │  │ etcd      │  │Scheduler │  │Controller │  │
│  │ Server   │  │ (storage) │  │          │  │ Manager   │  │
│  └──────────┘  └───────────┘  └──────────┘  └───────────┘  │
└─────────────────────────────────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   WORKER NODE   │ │   WORKER NODE   │ │   WORKER NODE   │
│  ┌───────────┐  │ │  ┌───────────┐  │ │  ┌───────────┐  │
│  │  kubelet  │  │ │  │  kubelet  │  │ │  │  kubelet  │  │
│  ├───────────┤  │ │  ├───────────┤  │ │  ├───────────┤  │
│  │kube-proxy │  │ │  │kube-proxy │  │ │  │kube-proxy │  │
│  ├───────────┤  │ │  ├───────────┤  │ │  ├───────────┤  │
│  │ Container │  │ │  │ Container │  │ │  │ Container │  │
│  │ Runtime   │  │ │  │ Runtime   │  │ │  │ Runtime   │  │
│  └───────────┘  │ │  └───────────┘  │ │  └───────────┘  │
│  ┌─────┐┌─────┐ │ │  ┌─────┐┌─────┐ │ │  ┌─────┐       │
│  │ Pod ││ Pod │ │ │  │ Pod ││ Pod │ │ │  │ Pod │       │
│  └─────┘└─────┘ │ │  └─────┘└─────┘ │ │  └─────┘       │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

### Key Concepts

| Concept        | Description                                                  |
| -------------- | ------------------------------------------------------------ |
| **Pod**        | Smallest deployable unit; one or more containers             |
| **Deployment** | Manages ReplicaSets; handles rolling updates                 |
| **Service**    | Stable network endpoint to access pods                       |
| **Namespace**  | Virtual cluster for isolation                                |
| **ConfigMap**  | External configuration data                                  |
| **Secret**     | Sensitive data (passwords, tokens)                           |
| **Ingress**    | HTTP routing (host/path-based) into the cluster              |

---

## Prerequisites: Local Kubernetes Setup

```bash
# Option 1: Docker Desktop (enable Kubernetes in settings)
# Option 2: minikube
minikube start --driver=docker

# Option 3: kind (Kubernetes IN Docker)
kind create cluster --name workshop

# Verify your cluster is running
kubectl cluster-info
kubectl get nodes
```

---

## Demo 1: kubectl Basics

```bash
# Cluster info
kubectl cluster-info
kubectl get nodes
kubectl get nodes -o wide

# View all resources in default namespace
kubectl get all

# View all namespaces
kubectl get namespaces

# View resources in a specific namespace
kubectl get pods -n kube-system

# Explain a resource type (built-in docs!)
kubectl explain pod
kubectl explain pod.spec.containers
```

---

## Demo 2: Your First Pod (Imperative)

```bash
# Run a pod directly (imperative style)
kubectl run my-nginx --image=nginx --port=80

# Check the pod
kubectl get pods
kubectl get pods -o wide

# Describe the pod (detailed info + events)
kubectl describe pod my-nginx

# View pod logs
kubectl logs my-nginx

# Execute into the pod
kubectl exec -it my-nginx -- bash
# Inside: curl localhost, then exit

# Port-forward to access from your machine
kubectl port-forward pod/my-nginx 8080:80
# Visit http://localhost:8080, then Ctrl+C

# Delete the pod
kubectl delete pod my-nginx
```

---

## Demo 3: Your First Pod (Declarative YAML)

Create `pod.yaml`:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: task-api
  labels:
    app: task-api
    environment: workshop
spec:
  containers:
    - name: api
      image: python:3.12-slim
      command: ["python", "-m", "http.server", "8000"]
      ports:
        - containerPort: 8000
      resources:
        requests:
          memory: "64Mi"
          cpu: "100m"
        limits:
          memory: "128Mi"
          cpu: "250m"
```

```bash
# Apply the YAML
kubectl apply -f pod.yaml

# View it
kubectl get pods
kubectl describe pod task-api

# Port forward and test
kubectl port-forward pod/task-api 8000:8000
# Visit http://localhost:8000

# Delete
kubectl delete -f pod.yaml
```

---

## Demo 4: Namespaces

```bash
# Create a namespace
kubectl create namespace workshop

# Run a pod in the namespace
kubectl run nginx --image=nginx -n workshop

# List pods in the namespace
kubectl get pods -n workshop

# Set default namespace for current context
kubectl config set-context --current --namespace=workshop
kubectl get pods  # Now shows workshop namespace

# Reset to default
kubectl config set-context --current --namespace=default

# Clean up
kubectl delete namespace workshop
```

---

## Demo 5: Labels and Selectors

```bash
# Create pods with labels
kubectl run frontend --image=nginx --labels="app=web,tier=frontend"
kubectl run backend --image=nginx --labels="app=web,tier=backend"
kubectl run database --image=nginx --labels="app=web,tier=database"

# List with labels shown
kubectl get pods --show-labels

# Filter by label
kubectl get pods -l tier=frontend
kubectl get pods -l app=web
kubectl get pods -l "tier in (frontend,backend)"
kubectl get pods -l "tier!=database"

# Add a label to existing pod
kubectl label pod frontend version=v1

# Remove a label
kubectl label pod frontend version-

# Clean up
kubectl delete pods frontend backend database
```

---

## Imperative vs Declarative

| Imperative                           | Declarative                          |
| ------------------------------------ | ------------------------------------ |
| `kubectl run nginx --image=nginx`    | `kubectl apply -f pod.yaml`          |
| Quick for testing                    | Reproducible, version-controlled     |
| Hard to track changes                | Git-friendly                         |
| **Use for**: learning, debugging     | **Use for**: production, CI/CD       |

---

## Exercises for Participants

1. Create a namespace called `dev` and deploy an nginx pod into it
2. Create a pod with labels `app=api`, `version=v2` and filter pods by these labels
3. Use `kubectl explain` to explore the `pod.spec.containers` fields
4. Port-forward a pod and access it from your browser

---

## Quick Reference

```bash
kubectl get RESOURCE                   # List resources
kubectl describe RESOURCE NAME         # Detailed info
kubectl apply -f FILE.yaml             # Create/update from YAML
kubectl delete -f FILE.yaml            # Delete from YAML
kubectl logs POD [-f]                  # View pod logs
kubectl exec -it POD -- COMMAND        # Execute in pod
kubectl port-forward POD LOCAL:REMOTE  # Forward port
kubectl explain RESOURCE               # Built-in docs
kubectl get pods --show-labels         # Show labels
kubectl get pods -l KEY=VALUE          # Filter by label
```
